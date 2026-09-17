"""EPP transport + response parsing for the .de test suite.

Stdlib only. Framing follows RFC 5734: a 4-byte big-endian length prefix
that includes the 4 header bytes themselves.
"""
from __future__ import annotations

import os
import re
import socket
import ssl
import struct
import time

EPP_NS = "urn:ietf:params:xml:ns:epp-1.0"
DOM_NS = "urn:ietf:params:xml:ns:domain-1.0"
CT_NS = "urn:ietf:params:xml:ns:contact-1.0"
SECDNS_NS = "urn:ietf:params:xml:ns:secDNS-1.1"
POLL_NS = "urn:ietf:params:xml:ns:poll-1.0"


def load_env(path):
    """Parse a KEY=VALUE env file. Real environment variables override it."""
    env = {}
    if not os.path.exists(path):
        raise SystemExit(f"env file not found: {path} (create it - see README)")
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            env[key.strip()] = val.strip().strip('"').strip("'")
    # Real environment variables take precedence (CI / secret injection).
    for key in list(env):
        if key in os.environ:
            env[key] = os.environ[key]
    return env


class SessionDead(Exception):
    """The EPP session is unusable (I/O error, timeout, server close)."""


class Response:
    """Best-effort parse of an EPP <response>.

    Regex-based so even a malformed or non-EPP reply yields the diagnostic
    fields the checklist needs.
    """

    def __init__(self, raw=""):
        self.raw = raw or ""
        self.code = None
        self.msg = ""
        self.extvalue = ""
        self.resdata = ""
        self.cltrid = ""
        self.svtrid = ""
        self.denic_codes = []
        self._parse()

    def _parse(self):
        # The registry/translation layer may namespace-prefix every tag
        # (e.g. <epp:result>, <epp:msg>), so each pattern tolerates an
        # optional "prefix:" before the tag name; the negative lookahead
        # keeps <msg> from matching a <message>-style tag.
        m = re.search(
            r'<(?:[A-Za-z0-9_-]+:)?result(?![A-Za-z0-9_-])[^>]*\bcode="(\d+)"',
            self.raw,
        )
        if m:
            self.code = m.group(1)
        m = re.search(
            r'<(?:[A-Za-z0-9_-]+:)?msg(?![A-Za-z0-9_-])[^>]*>'
            r'(.*?)</(?:[A-Za-z0-9_-]+:)?msg>',
            self.raw, re.S,
        )
        if m:
            self.msg = m.group(1).strip()
        m = re.search(
            r'<(?:[A-Za-z0-9_-]+:)?extValue[^>]*>(.*?)'
            r'</(?:[A-Za-z0-9_-]+:)?extValue>',
            self.raw, re.S,
        )
        if m:
            self.extvalue = m.group(1).strip()
        self.resdata = "\n".join(
            re.findall(
                r'<(?:[A-Za-z0-9_-]+:)?resData[^>]*>(.*?)'
                r'</(?:[A-Za-z0-9_-]+:)?resData>',
                self.raw, re.S,
            )
        )
        m = re.search(
            r'<(?:[A-Za-z0-9_-]+:)?clTRID[^>]*>(.*?)'
            r'</(?:[A-Za-z0-9_-]+:)?clTRID>',
            self.raw, re.S,
        )
        if m:
            self.cltrid = m.group(1).strip()
        m = re.search(
            r'<(?:[A-Za-z0-9_-]+:)?svTRID[^>]*>(.*?)'
            r'</(?:[A-Za-z0-9_-]+:)?svTRID>',
            self.raw, re.S,
        )
        if m:
            self.svtrid = m.group(1).strip()
        # The translation layer reports the original registry code as
        # "DENIC <11-digit>: <text>" in msg/extValue.
        self.denic_codes = sorted(set(re.findall(r'DENIC (\d{11})', self.raw)))

    @property
    def ok(self):
        return bool(self.code) and self.code.startswith("1")

    @property
    def parsed(self):
        return self.code is not None

    def describe(self):
        if not self.code:
            return "no EPP result code found in response"
        bits = [f"EPP {self.code}"]
        if self.msg:
            bits.append(f'"{self.msg}"')
        if self.denic_codes:
            bits.append(f"(DENIC {', '.join(self.denic_codes)})")
        return " ".join(bits)

    def avail(self):
        """Return '0'/'1' for domain:chk/contact:chk data, or None.

        Standard EPP carries availability as the ``domain:name/@avail``
        attribute; the OTE translation layer instead emits ``<domain:avail>``
        as a sibling element. Accept both so the suite keeps working, and let
        callers surface the deviation via :meth:`avail_is_element`.
        """
        m = re.search(r'\bavail="([01])"', self.resdata)
        if m:
            return m.group(1)
        m = re.search(r'<(?:[A-Za-z0-9_-]+:)?avail\b[^>]*>\s*([01])\s*<', self.resdata)
        if m:
            return m.group(1)
        return None

    def avail_is_element(self):
        """True when avail was only present in the non-standard sibling-element form."""
        if re.search(r'\bavail="[01]"', self.resdata):
            return False
        return bool(re.search(r'<(?:[A-Za-z0-9_-]+:)?avail\b[^>]*>\s*[01]\s*<', self.resdata))


class EPPSession:
    """One TCP+TLS EPP session (RFC 5734 framing, greeting read on connect)."""

    def __init__(self, host, port, timeout=45):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.dead = False
        self.dead_reason = ""
        self.greeting = ""
        try:
            self.sock = ctx.wrap_socket(
                socket.create_connection((host, port), timeout=timeout),
                server_hostname=host,
            )
            self.sock.settimeout(timeout)
            self.greeting = self._read_frame()
        except Exception as e:
            self.dead = True
            self.dead_reason = f"{type(e).__name__}: {e}"
            raise

    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("server closed connection while reading")
            buf += chunk
        return buf

    def _read_frame(self):
        (length,) = struct.unpack("!I", self._recv_exact(4))
        return self._recv_exact(length - 4).decode("utf-8", "replace")

    def _write_frame(self, xml):
        data = xml.encode("utf-8")
        self.sock.sendall(struct.pack("!I", len(data) + 4) + data)

    @staticmethod
    def wrap(inner, cltrid):
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<epp xmlns="{ns}"><command>{inner}<clTRID>{cid}</clTRID></command></epp>'
        ).format(ns=EPP_NS, inner=inner, cid=cltrid)

    def request(self, inner, label=""):
        """Send a wrapped EPP command and return the parsed Response.

        Raises SessionDead on any transport failure; the session is marked
        dead so the runner can block remaining work on this session.
        """
        if self.dead:
            raise SessionDead(self.dead_reason)
        cltrid = f"SUITE-{int(time.time())}-{_seq.next()}"
        xml = self.wrap(inner, cltrid)
        try:
            self._write_frame(xml)
            raw = self._read_frame()
        except Exception as e:
            self.dead = True
            self.dead_reason = f"{type(e).__name__}: {e} (on {label or inner[:48]})"
            self.close()
            raise SessionDead(self.dead_reason) from e
        resp = Response(raw)
        resp.request_xml = xml
        return resp

    def greeting_services(self):
        """(services, extensions) advertised in the server greeting.

        Tolerates namespace-prefixed tags (e.g. <epp:objURI>).
        """
        svcs = re.findall(
            r'<(?:[A-Za-z0-9_-]+:)?objURI>([^<]+)</(?:[A-Za-z0-9_-]+:)?objURI>',
            self.greeting or "",
        )
        exts = re.findall(
            r'<(?:[A-Za-z0-9_-]+:)?extURI>([^<]+)</(?:[A-Za-z0-9_-]+:)?extURI>',
            self.greeting or "",
        )
        return svcs, exts

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


# Module-level counter for unique clTRIDs within one process.
class _Counter:
    def __init__(self):
        self.n = 0

    def next(self):
        self.n += 1
        return self.n


_seq = _Counter()


def login_xml(user, pw, services, extensions=()):
    svc = "".join(f"<objURI>{s}</objURI>" for s in services)
    ext = ""
    if extensions:
        ext = "<svcExtension>" + "".join(
            f"<extURI>{e}</extURI>" for e in extensions
        ) + "</svcExtension>"
    return (
        "<login>"
        f"<clID>{user}</clID><pw>{pw}</pw>"
        "<options><version>1.0</version><lang>en</lang></options>"
        f"<svcs>{svc}{ext}</svcs>"
        "</login>"
    )
