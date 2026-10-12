"""Generate a syntactically valid DS record for secDNS tests.

A DS record is derived from a DNSKEY:

    DS = owner-name (wire form) || key tag (2) || algorithm (1) ||
         digest type (1) || digest

with the digest computed over the canonical DNSKEY RDATA
(flags(2) protocol(1) algorithm(1) public-key).

This module builds a fresh RSA-style DNSKEY (random modulus, exponent
65537, algorithm RSASHA256 = 8, flags 256) and derives the matching DS
digest. The public key is not cryptographically meaningful for testing
purposes - the registry does not verify it - but every field is
structurally valid, which is what secDNS validation cares about.

Stdlib only.
"""
from __future__ import annotations

import hashlib
import secrets
import struct

# DNSSEC algorithm 8 = RSASHA256
ALG = 8
# DS digest type 2 = SHA-256
DIGEST_TYPE = 2
# Zone key (ZSK) flags.
FLAGS = 256
PROTOCOL = 3


def _key_tag(flags: int, protocol: int, algorithm: int, public: bytes) -> int:
    """RFC 4034 section 3.2.1 key tag over the DNSKEY RDATA."""
    rdata = struct.pack(">HBB", flags, protocol, algorithm) + public
    acc = 0
    for i in range(0, len(rdata), 2):
        acc += (rdata[i] << 8) + rdata[i + 1]
    acc += (acc >> 16) & 0xFFFF
    acc += (acc >> 16) & 0xFFFF
    return acc & 0xFFFF


def _owner_wire(owner: str) -> bytes:
    """Encode an absolute owner name (e.g. ``example.wien``) in DNS wire format."""
    parts = owner.rstrip(".").split(".")
    out = b"".join(bytes([len(p)]) + p.encode("ascii") for p in parts)
    return out + b"\x00"


class DSRecord:
    """A syntactically valid DNSKEY + derived DS record."""

    def __init__(self, owner: str):
        self.owner = owner
        self.alg = ALG
        self.digest_type = DIGEST_TYPE
        # 2048-bit random RSA public key: exponent first (0x0100 01 = 65537),
        # then 256 random bytes with the high bit set to keep the key 2048-bit.
        modulus = secrets.token_bytes(256)
        modulus = bytes([modulus[0] | 0x80]) + modulus[1:]
        self.public = b"\x03\x01\x00\x01" + modulus
        self.key_tag = _key_tag(FLAGS, PROTOCOL, ALG, self.public)
        rdata = struct.pack(">HBB", FLAGS, PROTOCOL, ALG) + self.public
        self.digest = hashlib.sha256(
            _owner_wire(owner) + bytes([ALG, DIGEST_TYPE]) + rdata
        ).hexdigest()

    def sec_dns_add_xml(self, ns_prefix="secDNS"):
        return (
            f"<{ns_prefix}:dsData>"
            f"<{ns_prefix}:keyTag>{self.key_tag}</{ns_prefix}:keyTag>"
            f"<{ns_prefix}:alg>{ALG}</{ns_prefix}:alg>"
            f"<{ns_prefix}:digestType>{DIGEST_TYPE}</{ns_prefix}:digestType>"
            f"<{ns_prefix}:digest>{self.digest}</{ns_prefix}:digest>"
            f"</{ns_prefix}:dsData>"
        )
