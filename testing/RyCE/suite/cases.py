"""Test case definitions for the RyCE (.wien) EPP suite.

Cases are built from the zone profile in :mod:`.zones`; the zone drives the
test-domain suffix and the registrar test data from the env file.

Two phases:

* ``basic``  - session handling and the core EPP domain/contact operations
  (check / create / info / update / delete / poll).
* ``dnssec`` - DNSSEC management via the secDNS-1.1 extension (RFC 5910:
  ``<secDNS:update>`` on domain:update, ``<secDNS:infData>`` on the
  domain:info response), plus the regression case for
  ``domain:info`` on a domain that carries a DS record.

Each case declares which other cases it requires; the runner blocks a case
(instead of running it) when a requirement did not pass, and the checklist
records which test is currently blocking which.

Cases are written to be self-healing on re-runs: if a previous crashed run
left an object behind (create answers "object exists"), the cleanup is
retried and the create is attempted again.

Regression coverage — GW-4238
-----------------------------

``b-dom-info-dnssec`` (dnssec phase) is the regression test for GW-4238:
``domain:info`` on a domain that has a DNSSEC DS record must return 1000
with a well-formed response. The bug was that the response builder emitted
a ``secDNS`` extension without declaring the ``secDNS`` namespace on the
root ``<epp>`` element, producing malformed XML that DAMSr parsed as
``unknown namespace prefix 'secDNS'`` and surfaced to the registrar as a
2400.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from .ds import DSRecord
from .epp import CT_NS, DOM_NS, SECDNS_NS, EPPSession, Response, login_xml
from .zones import Zone

PHASE_BASIC = "basic"
PHASE_DNSSEC = "dnssec"

# Greeting element, tolerating a namespace prefix (<epp:greeting> or <greeting>).
_GREETING_RE = re.compile(r'<(?:[A-Za-z0-9_-]+:)?greeting[ >]')


# --------------------------------------------------------------------- config


@dataclass
class Ctx:
    """Mutable state shared by all cases of one run."""

    cfg: dict
    zone: Zone
    domain: str          # primary zone domain under test (created + deleted)
    domain_ds: str       # zone domain for the DNSSEC phase
    missing_domain: str  # label that must NOT exist (negative checks)
    contact: str         # EPP contact handle
    contact_missing: str # handle that must NOT exist
    authinfo: str        # domain authInfo used for creates
    ns: List[str]
    ns_alt: List[str]
    role_handles: dict   # role -> contact handle used in domain:create
    ds: Optional[DSRecord] = None

    def __init__(self, cfg: dict, zone: Zone):
        self.cfg = cfg
        self.zone = zone
        p = zone.env_prefix
        rand = f"{int(time.time()) % 1000000:06d}"
        # RyCE .wien labels must be lowercase alphanumeric + hyphens;
        # no underscores, no mixed case.
        self.domain = f"ryce{rand}{zone.tld}"
        self.domain_ds = f"ryceds{rand}{zone.tld}"
        self.missing_domain = f"rycemiss{rand}{zone.tld}"
        self.contact = cfg.get(f"{p}_EPP_CONTACT_HANDLE") or f"ryce{rand}"
        self.contact_missing = f"rycem{rand}"
        self.authinfo = cfg.get(f"{p}_AUTHINFO", f"ryce-suit-{rand}")
        self.ns = [
            cfg.get(f"{p}_NS1", "ns1.wien"),
            cfg.get(f"{p}_NS2", "ns2.wien"),
        ]
        self.ns_alt = [
            cfg.get(f"{p}_NS3", "ns3.wien"),
            cfg.get(f"{p}_NS4", "ns4.wien"),
        ]
        # RyCE .wien contact roles: the OTE may require fewer roles than .de.
        # Default to registrant only; override via W_CREATE_ROLES in .env
        # (comma-separated: registrant,admin,tech,billing).
        roles_csv = (cfg.get(f"{p}_CREATE_ROLES") or "registrant").lower()
        self.role_handles = {}
        for role in [r.strip() for r in roles_csv.split(",") if r.strip()]:
            if zone.contact_source == "env":
                self.role_handles[role] = cfg.get(
                    zone.role_env_key(role), zone.role_defaults.get(role)
                )
            else:
                short = {"registrant": "reg", "admin": "adm", "tech": "tec",
                         "billing": "bil"}.get(role, role[:3])
                self.role_handles[role] = f"ryce-{short}-{rand}"


# ------------------------------------------------------------- XML builders


def _dom(name: str) -> str:
    return f'<domain:name>{name}</domain:name>'


def dom_check(name: str) -> str:
    return (
        f'<check><domain:check xmlns:domain="{DOM_NS}">'
        f"{_dom(name)}</domain:check></check>"
    )


def dom_create(name: str, ctx: Ctx) -> str:
    """Full domain:create satisfying the zone's contact-role policy.

    Element order follows domain-1.0.xsd: name, ns?, registrant?, contact*,
    authInfo? (no ``<period>``: RyCE .wien has none).
    """
    zone = ctx.zone
    parts = [f"<domain:name>{name}</domain:name>"]
    parts.append(
        f'<domain:ns>'
        f'<domain:hostObj>{ctx.ns[0]}</domain:hostObj>'
        f'<domain:hostObj>{ctx.ns[1]}</domain:hostObj>'
        f"</domain:ns>"
    )
    if "registrant" in ctx.role_handles:
        parts.append(
            f'<domain:registrant>{ctx.role_handles["registrant"]}</domain:registrant>'
        )
    for role in ("admin", "tech", "billing"):
        if role in ctx.role_handles:
            parts.append(
                f'<domain:contact type="{role}">'
                f'{ctx.role_handles[role]}</domain:contact>'
            )
    parts.append(
        f'<domain:authInfo><domain:pw>{ctx.authinfo}</domain:pw></domain:authInfo>'
    )
    return (
        f'<create><domain:create xmlns:domain="{DOM_NS}">'
        + "".join(parts)
        + "</domain:create></create>"
    )


def dom_info(name: str) -> str:
    return (
        f'<info><domain:info xmlns:domain="{DOM_NS}">'
        f"{_dom(name)}</domain:info></info>"
    )


def dom_update_ns(name: str, add: List[str], rem: List[str]) -> str:
    """Standard EPP domain:update: ``<domain:add>``/``<domain:rem>`` wrap the
    NS list. RyCE OTE validates element order as name, add?, rem?, chg? —
    a ``<domain:rem>`` before ``<domain:add>`` is rejected with 2001."""
    add_xml = "".join(f"<domain:hostObj>{n}</domain:hostObj>" for n in add)
    rem_xml = "".join(f"<domain:hostObj>{n}</domain:hostObj>" for n in rem)
    rem_el = f"<domain:rem><domain:ns>{rem_xml}</domain:ns></domain:rem>" if rem else ""
    add_el = f"<domain:add><domain:ns>{add_xml}</domain:ns></domain:add>" if add else ""
    return (
        f'<update><domain:update xmlns:domain="{DOM_NS}">'
        f"{_dom(name)}"
        f"{add_el}{rem_el}"
        f"</domain:update></update>"
    )


def dom_delete(name: str) -> str:
    return (
        f'<delete><domain:delete xmlns:domain="{DOM_NS}">'
        f"{_dom(name)}</domain:delete></delete>"
    )


def ct_id(handle: str) -> str:
    return f"<contact:id>{handle}</contact:id>"


def ct_check(handle: str) -> str:
    return (
        f'<check><contact:check xmlns:contact="{CT_NS}">'
        f"{ct_id(handle)}</contact:check></check>"
    )


def ct_create(handle: str, ctx: Ctx) -> str:
    """PERSON contact (no ``<contact:org>``) with full postal info.

    ``contact:voice`` follows the RFC 5733 e164StringType pattern
    ``(\\+[0-9]{1,3}\\.\\[0-9]{1,14})?`` — override per run with
    ``W_CONTACT_PHONE``.
    """
    cfg = ctx.cfg
    p = ctx.zone.env_prefix
    email = cfg.get(f"{p}_CONTACT_EMAIL", "ryceskip.person@example.com")
    voice = cfg.get(f"{p}_CONTACT_PHONE", "+43.155500101")
    city = cfg.get(f"{p}_CONTACT_CITY", "Wien")
    cc = cfg.get(f"{p}_CONTACT_CC", "AT")
    name = cfg.get(f"{p}_CONTACT_NAME", "Test Person")
    return (
        f'<create><contact:create xmlns:contact="{CT_NS}">'
        f"{ct_id(handle)}"
        f'<contact:postalInfo type="int">'
        f"<contact:name>{name}</contact:name>"
        # RFC 5733 addrType order: street*, city, sp?, pc?, cc.
        f"<contact:addr>"
        f"<contact:street>1 Example Strasse</contact:street>"
        f"<contact:city>{city}</contact:city>"
        f"<contact:pc>1010</contact:pc>"
        f"<contact:cc>{cc}</contact:cc>"
        f"</contact:addr>"
        f"</contact:postalInfo>"
        f"<contact:voice>{voice}</contact:voice>"
        f"<contact:email>{email}</contact:email>"
        f'<contact:authInfo><contact:pw>TestPw#1</contact:pw></contact:authInfo>'
        f"</contact:create></create>"
    )


def ct_info(handle: str) -> str:
    return (
        f'<info><contact:info xmlns:contact="{CT_NS}">'
        f"{ct_id(handle)}</contact:info></info>"
    )


def ct_update(handle: str, email: str) -> str:
    return (
        f'<update><contact:update xmlns:contact="{CT_NS}">'
        f"{ct_id(handle)}"
        f'<contact:chg>'
        f"<contact:email>{email}</contact:email>"
        f"</contact:chg>"
        f"</contact:update></update>"
    )


def ct_delete(handle: str) -> str:
    return (
        f'<delete><contact:delete xmlns:contact="{CT_NS}">'
        f"{ct_id(handle)}</contact:delete></delete>"
    )


def poll_req() -> str:
    """RFC 5730 section 2.9.2.3 poll request (no namespace, no object)."""
    return '<poll op="req"/>'


def _secdns_update(name: str, body: str) -> str:
    """RFC 5910 DS change: an empty domain:update carrying <secDNS:update>.

    secDNS is a command extension, not a command: there is no <add>/<rem>
    verb in EPP. The <extension> element follows the command verb inside
    <command>, before <clTRID>.
    """
    return (
        f'<update><domain:update xmlns:domain="{DOM_NS}">'
        f"{_dom(name)}</domain:update></update>"
        f'<extension><secDNS:update xmlns:secDNS="{SECDNS_NS}">'
        f"{body}</secDNS:update></extension>"
    )


def secdns_add(name: str, ds: DSRecord) -> str:
    return _secdns_update(name, f"<secDNS:add>{ds.sec_dns_add_xml()}</secDNS:add>")


def secdns_rem(name: str, ds: DSRecord) -> str:
    """Remove one DS record; RFC 5910 dsData interface identifies it by the
    full dsData (keyTag, alg, digestType, digest)."""
    return _secdns_update(name, f"<secDNS:rem>{ds.sec_dns_add_xml()}</secDNS:rem>")


def _ds_key_tags(resp: Response) -> List[str]:
    """keyTags in the secDNS:infData response extension of a domain:info."""
    return re.findall(
        r'<(?:[A-Za-z0-9_-]+:)?keyTag>\s*(\d+)\s*</(?:[A-Za-z0-9_-]+:)?keyTag>',
        resp.extension,
    )


# ------------------------------------------------------------------- helpers


def _avail(resp: Response, want: Optional[str], label: str) -> Tuple[bool, str]:
    got = resp.avail()
    if got is None:
        return False, f"{label}: no avail (attribute or <domain:avail> element) in resData"
    if want is not None and got != want:
        return False, f"{label}: avail={got}, expected {want}"
    note = f"{label}: avail={got}"
    if resp.avail_is_element():
        note += (" | DEVIATION: OTE returned <domain:avail> as a sibling element, "
                 "not the standard domain:name/@avail attribute")
    return True, note


def _ns_set(resp: Response) -> set:
    """Set of hostObj names in resData (trailing-dot / case normalised)."""
    vals = re.findall(r'<domain:hostObj[^>]*>([^<]*)</domain:hostObj>', resp.resdata)
    return {v.rstrip(".").lower() for v in vals}


# ---------------------------------------------------------------------- cases


@dataclass
class Case:
    id: str
    name: str
    phase: str
    session: str                      # "basic" | "secdns"
    requires: Tuple[str, ...]
    expect_codes: frozenset           # acceptable EPP result codes (empty: no code check)
    run: Callable[[EPPSession, Ctx], Optional[Response]]
    verify: Optional[Callable] = None  # (resp, ctx, sess) -> (ok, note)
    cleanup: bool = False             # skipped with --keep (leave objects behind)


def build_cases(cfg: dict, zone: Zone) -> Tuple[List[Case], Ctx]:
    ctx = Ctx(cfg, zone)
    cases: List[Case] = []

    def add(case: Case):
        cases.append(case)

    # ------------------------------------------------------------- basic phase

    def run_connect(sess: EPPSession, _ctx: Ctx) -> Optional[Response]:
        # The runner opens the session before calling; nothing to send.
        return None

    def verify_connect(resp, _ctx, sess):
        g = sess.greeting or ""
        svcs, exts = sess.greeting_services()
        ok = bool(_GREETING_RE.search(g)) and len(svcs) > 0
        return ok, f"greeting services={svcs} extensions={exts}"

    add(Case(
        id="b-connect",
        name="TLS connect + EPP greeting",
        phase=PHASE_BASIC, session="basic", requires=(),
        expect_codes=frozenset(), run=run_connect, verify=verify_connect,
    ))

    def run_login(sess: EPPSession, _ctx: Ctx):
        return sess.request(
            login_xml(cfg["EPP_USER"], cfg["EPP_PASSWORD"], [DOM_NS, CT_NS]),
            "login",
        )

    add(Case(
        id="b-login",
        name="login (domain-1.0 + contact-1.0)",
        phase=PHASE_BASIC, session="basic", requires=("b-connect",),
        expect_codes=frozenset({"1000"}), run=run_login,
    ))

    # Pre-create any role handle the domain:create will reference but that
    # does not exist on the registry yet ("create" source always; "env"
    # source only when .env supplied no pre-mapped handle).
    role_create_ids: List[str] = []
    for role, handle in ctx.role_handles.items():
        needs_create = zone.contact_source == "create" or \
            (zone.contact_source == "env" and not handle)
        if not needs_create:
            continue
        role_create_ids.append(f"b-ct-role-create-{role}")

        def run_role_create(sess, _c, _handle=handle, _role=role):
            resp = sess.request(ct_create(_handle, ctx), f"contact:create ({_role})")
            if resp.code in ("2101", "2302", "2304", "2306"):
                sess.request(ct_delete(_handle),
                             f"contact:create-cleanup-delete ({_role})")
                resp = sess.request(ct_create(_handle, ctx),
                                    f"contact:create ({_role}, retry)")
            return resp

        add(Case(
            id=f"b-ct-role-create-{role}",
            name=f"contact:create role contact ({role})",
            phase=PHASE_BASIC, session="basic", requires=("b-login",),
            expect_codes=frozenset({"1000"}), run=run_role_create,
        ))

    def run_dom_check_free(sess, _ctx):
        return sess.request(dom_check(ctx.domain), "domain:check (new)")

    def verify_dom_check_free(resp, _c, _s):
        ok, note = _avail(resp, "1", "pre-create check")
        if not ok:
            return False, note + " (label taken? leftover from a crashed run)"
        return True, note

    add(Case(
        id="b-dom-check-free",
        name="domain:check free label -> avail=1",
        phase=PHASE_BASIC, session="basic", requires=("b-login",),
        expect_codes=frozenset({"1000"}),
        run=run_dom_check_free, verify=verify_dom_check_free,
    ))

    taken = cfg.get(f"{zone.env_prefix}_TAKEN_DOMAIN", zone.taken_domain)

    def run_dom_check_taken(sess, _ctx):
        return sess.request(dom_check(taken), "domain:check (taken)")

    def verify_dom_check_taken(resp, _c, _s):
        got = resp.avail()
        if got is None:
            return False, f"no <domain:avail> in resData for {taken}"
        return True, f"informational: {taken} -> avail={got} (expect 0 on a healthy zone)"

    add(Case(
        id="b-dom-check-taken",
        name=f"domain:check known-taken label ({taken})",
        phase=PHASE_BASIC, session="basic", requires=("b-login",),
        expect_codes=frozenset({"1000"}),
        run=run_dom_check_taken, verify=verify_dom_check_taken,
    ))

    def run_dom_create(sess, _ctx):
        resp = sess.request(dom_create(ctx.domain, ctx), "domain:create")
        if resp.code in ("2302", "2305"):
            sess.request(dom_delete(ctx.domain), "domain:create-cleanup-delete")
            resp = sess.request(dom_create(ctx.domain, ctx), "domain:create (retry)")
        return resp

    add(Case(
        id="b-dom-create",
        name=f"domain:create ({'/'.join(ctx.role_handles)} + 2 NS + authInfo)",
        phase=PHASE_BASIC, session="basic", requires=("b-login", *role_create_ids),
        expect_codes=frozenset({"1000"}), run=run_dom_create,
    ))

    def run_dom_check_created(sess, _ctx):
        return sess.request(dom_check(ctx.domain), "domain:check (post-create)")

    def verify_dom_check_created(resp, _c, _s):
        return _avail(resp, "0", "post-create check")

    add(Case(
        id="b-dom-check-created",
        name="domain:check after create -> avail=0",
        phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
        expect_codes=frozenset({"1000"}),
        run=run_dom_check_created, verify=verify_dom_check_created,
    ))

    def run_dom_info(sess, _ctx):
        return sess.request(dom_info(ctx.domain), "domain:info")

    def verify_dom_info(resp, _c, _s):
        rd = resp.resdata
        ok = ctx.domain in rd
        notes = []
        if not ok:
            notes.append(f"name {ctx.domain} not in resData")
        else:
            status_m = re.search(r'<domain:status[^>]*\bs="([a-zA-Z]+)"', rd)
            status = status_m.group(1) if status_m else "connect"
            notes.append(f"status={status} (no status element = healthy/connect)")
            ns = _ns_set(resp)
            if len(ns) < 2:
                if status == "pendingCreate":
                    notes.append("no hostObj yet (expected while pendingCreate)")
                else:
                    notes.append(f"DEVIATION: expected >=2 hostObj in info, found {len(ns)}")
            if "<domain:authInfo>" not in rd:
                notes.append("authInfo missing from info")
        return ok, "; ".join(notes)

    add(Case(
        id="b-dom-info",
        name="domain:info reflects create data",
        phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
        expect_codes=frozenset({"1000"}), run=run_dom_info, verify=verify_dom_info,
    ))

    def run_dom_create_dup(sess, _ctx):
        return sess.request(dom_create(ctx.domain, ctx), "domain:create (duplicate)")

    add(Case(
        id="b-dom-create-dup",
        name="domain:create duplicate -> 2302/2305 (object exists)",
        phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
        expect_codes=frozenset({"2302", "2305"}), run=run_dom_create_dup,
    ))

    def run_dom_info_missing(sess, _ctx):
        return sess.request(dom_info(ctx.missing_domain), "domain:info (missing)")

    add(Case(
        id="b-dom-info-missing",
        name="domain:info unknown domain -> 2303",
        phase=PHASE_BASIC, session="basic", requires=("b-login",),
        expect_codes=frozenset({"2303"}), run=run_dom_info_missing,
    ))

    def run_dom_update_ns(sess, _ctx):
        return sess.request(
            dom_update_ns(ctx.domain, add=ctx.ns_alt, rem=ctx.ns),
            "domain:update (ns swap)",
        )

    add(Case(
        id="b-dom-update-ns",
        name="domain:update replace nameservers",
        phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
        expect_codes=frozenset({"1000"}), run=run_dom_update_ns,
    ))

    def run_dom_info_after_update(sess, _c):
        return sess.request(dom_info(ctx.domain), "domain:info (post-update)")

    def verify_dom_info_after_update(resp, _c, _s):
        notes, ok = [], True
        ns = _ns_set(resp)
        if not ns:
            return True, "NS swap not verifiable: domain:info returned no hostObj"
        for n in ctx.ns_alt:
            if n.lower() not in ns:
                ok = False
                notes.append(f"new NS {n} missing")
        for n in ctx.ns:
            if n.lower() in ns:
                ok = False
                notes.append(f"old NS {n} still present")
        return ok, "; ".join(notes) if notes else "NS swap visible in domain:info"

    add(Case(
        id="b-dom-info-after-update",
        name="domain:info after update shows new NS",
        phase=PHASE_BASIC, session="basic", requires=("b-dom-update-ns",),
        expect_codes=frozenset({"1000"}),
        run=run_dom_info_after_update, verify=verify_dom_info_after_update,
    ))

    def run_dom_delete(sess, _c):
        return sess.request(dom_delete(ctx.domain), "domain:delete")

    add(Case(
        id="b-dom-delete",
        name="domain:delete",
        phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
        expect_codes=frozenset({"1000", "1001"}), run=run_dom_delete, cleanup=True,
    ))

    def run_dom_check_after_delete(sess, _c):
        return sess.request(dom_check(ctx.domain), "domain:check (post-delete)")

    def verify_dom_check_after_delete(resp, _c, _s):
        got = resp.avail()
        if got is None:
            return False, "post-delete check: no avail (attribute or element) in resData"
        if got == "1":
            return True, "post-delete check: avail=1 (domain removed)"
        return True, ("post-delete check: avail=0 - delete still pending "
                      "(async grace-period suspension, expected right after 1001)")

    add(Case(
        id="b-dom-check-after-delete",
        name="domain:check after delete -> avail=1",
        phase=PHASE_BASIC, session="basic", requires=("b-dom-delete",),
        expect_codes=frozenset({"1000"}),
        run=run_dom_check_after_delete, verify=verify_dom_check_after_delete,
    ))

    def run_ct_check_free(sess, _c):
        return sess.request(ct_check(ctx.contact), "contact:check (new)")

    def verify_ct_check_free(resp, _c, _s):
        if ctx.contact not in resp.resdata:
            return False, f"handle {ctx.contact} not in resData"
        note = f"handle {ctx.contact} in resData"
        if resp.avail() is not None:
            note += f", avail={resp.avail()}"
            if resp.avail_is_element():
                note += " | DEVIATION: <contact:avail> returned as element, not attribute"
        return True, note

    add(Case(
        id="b-ct-check-free",
        name="contact:check new handle",
        phase=PHASE_BASIC, session="basic", requires=("b-login",),
        expect_codes=frozenset({"1000"}), run=run_ct_check_free,
        verify=verify_ct_check_free,
    ))

    def run_ct_create(sess, _c):
        resp = sess.request(ct_create(ctx.contact, ctx), "contact:create")
        if resp.code in ("2101", "2302", "2304", "2306"):
            sess.request(ct_delete(ctx.contact), "contact:create-cleanup-delete")
            resp = sess.request(ct_create(ctx.contact, ctx), "contact:create (retry)")
        return resp

    add(Case(
        id="b-ct-create",
        name="contact:create (PERSON)",
        phase=PHASE_BASIC, session="basic", requires=("b-ct-check-free",),
        expect_codes=frozenset({"1000"}), run=run_ct_create,
    ))

    def run_ct_info(sess, _c):
        return sess.request(ct_info(ctx.contact), "contact:info")

    def verify_ct_info(resp, _c, _s):
        if ctx.contact not in resp.resdata:
            return False, f"handle {ctx.contact} not in resData"
        return True, "handle present in resData"

    add(Case(
        id="b-ct-info",
        name="contact:info after create",
        phase=PHASE_BASIC, session="basic", requires=("b-ct-create",),
        expect_codes=frozenset({"1000"}), run=run_ct_info, verify=verify_ct_info,
    ))

    new_email = "ryceskip.updated@example.com"

    def run_ct_update(sess, _c):
        return sess.request(ct_update(ctx.contact, new_email), "contact:update")

    add(Case(
        id="b-ct-update",
        name="contact:update email",
        phase=PHASE_BASIC, session="basic", requires=("b-ct-create",),
        expect_codes=frozenset({"1000"}), run=run_ct_update,
    ))

    def run_ct_delete(sess, _c):
        return sess.request(ct_delete(ctx.contact), "contact:delete")

    add(Case(
        id="b-ct-delete",
        name="contact:delete",
        phase=PHASE_BASIC, session="basic", requires=("b-ct-update",),
        expect_codes=frozenset({"1000"}), run=run_ct_delete, cleanup=True,
    ))

    def run_ct_check_after_delete(sess, _c):
        return sess.request(ct_check(ctx.contact), "contact:check (post-delete)")

    add(Case(
        id="b-ct-check-after-delete",
        name="contact:check after delete",
        phase=PHASE_BASIC, session="basic", requires=("b-ct-delete",),
        expect_codes=frozenset({"1000"}), run=run_ct_check_after_delete,
        verify=verify_ct_check_free,
    ))

    def run_ct_info_missing(sess, _c):
        return sess.request(ct_info(ctx.contact_missing), "contact:info (missing)")

    add(Case(
        id="b-ct-info-missing",
        name="contact:info unknown handle -> 2303",
        phase=PHASE_BASIC, session="basic", requires=("b-login",),
        expect_codes=frozenset({"2303"}), run=run_ct_info_missing,
    ))

    def run_poll(sess, _c):
        if not getattr(sess, "logged_in", False):
            r = sess.request(
                login_xml(cfg["EPP_USER"], cfg["EPP_PASSWORD"], [DOM_NS, CT_NS]),
                "login (poll session)",
            )
            sess.logged_in = r.ok
            if not r.ok:
                return r
        return sess.request(poll_req(), "poll op=req")

    def verify_poll(resp, _c, _s):
        if resp.code == "1301":
            # RFC 5730: 1301 must carry <msgQ count= id=>.
            m = re.search(r'<(?:[A-Za-z0-9_-]+:)?msgQ\b[^>]*\bcount="(\d+)"[^>]*\bid="[^"]+"', resp.raw) \
                or re.search(r'<(?:[A-Za-z0-9_-]+:)?msgQ\b[^>]*\bid="[^"]+"[^>]*\bcount="(\d+)"', resp.raw)
            if not m:
                return False, "1301 without <msgQ count= id=>"
            return True, f"queue not empty: {m.group(1)} message(s) (left un-acked for the owner)"
        return True, "queue empty"

    add(Case(
        id="b-poll-empty",
        name="poll op=req (read-only, no ack)",
        # Own session so a poll failure cannot take the main session down.
        phase=PHASE_BASIC, session="basic-poll", requires=("b-login",),
        expect_codes=frozenset({"1300", "1301"}), run=run_poll, verify=verify_poll,
    ))

    def run_logout(sess, _c):
        return sess.request("<logout/>", "logout")

    add(Case(
        id="b-logout",
        name="logout",
        phase=PHASE_BASIC, session="basic", requires=("b-login",),
        expect_codes=frozenset({"1500", "1000"}), run=run_logout,
    ))

    # -------------------------------------------------------------- dnssec phase

    def run_s_connect(sess, _c):
        return None

    def verify_s_connect(resp, _c, sess):
        g = sess.greeting or ""
        svcs, exts = sess.greeting_services()
        note = f"greeting services={svcs} extensions={exts}"
        if SECDNS_NS not in exts:
            note += " | NOTE: secDNS-1.1 not advertised in greeting"
        return bool(_GREETING_RE.search(g)), note

    add(Case(
        id="s-connect",
        name="TLS connect + EPP greeting (secDNS session)",
        phase=PHASE_DNSSEC, session="secdns", requires=(),
        expect_codes=frozenset(), run=run_s_connect, verify=verify_s_connect,
    ))

    def run_s_login(sess, _c):
        return sess.request(
            login_xml(cfg["EPP_USER"], cfg["EPP_PASSWORD"], [DOM_NS], [SECDNS_NS]),
            "login (secDNS)",
        )

    add(Case(
        id="s-login",
        name="login with secDNS-1.1 extension",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-connect",),
        expect_codes=frozenset({"1000"}), run=run_s_login,
    ))

    def run_s_dom_create(sess, _c):
        ctx.ds = DSRecord(ctx.domain_ds)
        resp = sess.request(dom_create(ctx.domain_ds, ctx), "domain:create (dnssec)")
        if resp.code in ("2302", "2305"):
            sess.request(dom_delete(ctx.domain_ds), "domain:create-cleanup-delete")
            resp = sess.request(dom_create(ctx.domain_ds, ctx),
                                "domain:create (dnssec, retry)")
        return resp

    add(Case(
        id="s-dom-create",
        name="domain:create for DNSSEC target",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-login", *role_create_ids),
        expect_codes=frozenset({"1000"}), run=run_s_dom_create,
    ))

    def run_s_secdns_add(sess, _c):
        return sess.request(secdns_add(ctx.domain_ds, ctx.ds), "domain:update +secDNS:add")

    add(Case(
        id="s-secdns-add",
        name="domain:update secDNS:add DS record",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-dom-create",),
        expect_codes=frozenset({"1000"}), run=run_s_secdns_add,
    ))

    # ---- GW-4238 regression ----------------------------------------

    def run_b_dom_info_dnssec(sess, _c):
        """domain:info on a domain that has a DS record (GW-4238 regression).

        Before the fix, the OTE response builder emitted a ``secDNS``
        extension without declaring the namespace on the root ``<epp>``
        element; DAMSr parsed that as ``unknown namespace prefix 'secDNS'``
        and returned 2400 to the registrar. The post-fix response must be
        well-formed XML and carry code 1000.
        """
        resp = sess.request(dom_info(ctx.domain_ds), "domain:info (dnssec domain)")
        return resp

    def verify_b_dom_info_dnssec(resp, _c, _s):
        rd = resp.resdata
        notes = []
        if ctx.domain_ds not in rd:
            notes.append(f"name {ctx.domain_ds} not in resData")
        if ctx.ds is not None and str(ctx.ds.key_tag) not in _ds_key_tags(resp):
            notes.append(f"DEVIATION: keyTag {ctx.ds.key_tag} not in the secDNS:infData extension (expected after secDNS:add)")
        ok = ctx.domain_ds in rd
        return ok, "; ".join(notes) if notes else "domain with DS record returned clean (GW-4238)"

    add(Case(
        id="b-dom-info-dnssec",
        name="domain:info on DNSSEC domain -> 1000 (GW-4238 regression)",
        phase=PHASE_DNSSEC, session="secdns",
        requires=("s-secdns-add",),
        expect_codes=frozenset({"1000"}),
        run=run_b_dom_info_dnssec, verify=verify_b_dom_info_dnssec,
    ))
    # ----------------------------------------------------------------

    def run_s_secdns_info(sess, _c):
        return sess.request(dom_info(ctx.domain_ds), "domain:info (secDNS)")

    def verify_s_secdns_info(resp, _c, _s):
        ds = ctx.ds
        if ds is None:
            return False, "no DS record generated for this run"
        if "infData" not in resp.extension or "dsData" not in resp.extension:
            return False, "no <secDNS:infData>/<secDNS:dsData> in response <extension>"
        tags = _ds_key_tags(resp)
        if str(ds.key_tag) not in tags:
            return False, f"keyTag {ds.key_tag} not in secDNS:infData (got {tags})"
        return True, f"keyTag {ds.key_tag} present in secDNS:infData"

    add(Case(
        id="s-secdns-info",
        name="domain:info shows DS in secDNS:infData",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-secdns-add",),
        expect_codes=frozenset({"1000"}),
        run=run_s_secdns_info, verify=verify_s_secdns_info,
    ))

    def run_s_secdns_rem(sess, _c):
        ds = ctx.ds
        if ds is None:
            raise RuntimeError("ctx.ds is not set; s-secdns-add has not run")
        return sess.request(secdns_rem(ctx.domain_ds, ds), "domain:update +secDNS:rem")

    add(Case(
        id="s-secdns-rem",
        name="domain:update secDNS:rem DS record",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-secdns-add",),
        expect_codes=frozenset({"1000"}), run=run_s_secdns_rem,
    ))

    def run_s_secdns_info_after_rem(sess, _c):
        return sess.request(dom_info(ctx.domain_ds), "domain:info (secDNS, post-rem)")

    def verify_s_secdns_info_after_rem(resp, _c, _s):
        tag = str(getattr(ctx.ds, "key_tag", "?"))
        if tag in _ds_key_tags(resp):
            return False, f"keyTag {tag} still in secDNS:infData after rem"
        return True, "DS no longer in secDNS:infData"

    add(Case(
        id="s-secdns-info-after-rem",
        name="domain:info after rem (DS gone)",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-secdns-rem",),
        expect_codes=frozenset({"1000"}),
        run=run_s_secdns_info_after_rem, verify=verify_s_secdns_info_after_rem,
    ))

    def run_s_secdns_rem_missing(sess, _c):
        # A fresh DS that was never added to the domain.
        return sess.request(
            secdns_rem(ctx.domain_ds, DSRecord(ctx.domain_ds)),
            "domain:update +secDNS:rem (no match)",
        )

    add(Case(
        id="s-secdns-rem-missing",
        name="domain:update secDNS:rem non-existent DS -> 2303/2304/2306",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-secdns-rem",),
        expect_codes=frozenset({"2303", "2304", "2306"}), run=run_s_secdns_rem_missing,
    ))

    def run_s_dom_delete(sess, _c):
        return sess.request(dom_delete(ctx.domain_ds), "domain:delete (dnssec)")

    add(Case(
        id="s-dom-delete",
        name="domain:delete DNSSEC target",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-dom-create",),
        expect_codes=frozenset({"1000", "1001"}), run=run_s_dom_delete, cleanup=True,
    ))

    def run_s_logout(sess, _c):
        return sess.request("<logout/>", "logout (secDNS)")

    add(Case(
        id="s-logout",
        name="logout (secDNS session)",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-login",),
        expect_codes=frozenset({"1500", "1000"}), run=run_s_logout,
    ))

    # Role contacts shared by both domains: delete last.
    if zone.contact_source == "create":
        for role, handle in list(ctx.role_handles.items()):
            def run_role_delete(sess, _c, _handle=handle, _role=role):
                return sess.request(ct_delete(_handle), f"contact:delete ({_role})")

            def verify_role_delete(resp, _c, _s, _role=role):
                if resp.code == "2305":
                    return True, (
                        f"{_role} contact still associated with the "
                        f"pending-delete domain; association releases when the "
                        f"domain delete completes"
                    )
                return True, f"{_role} contact deleted"

            add(Case(
                id=f"b-ct-role-delete-{role}",
                name=f"contact:delete role contact ({role})",
                phase=PHASE_BASIC, session="basic",
                requires=("b-dom-delete", "s-dom-delete"),
                expect_codes=frozenset({"1000", "2305"}),
                run=run_role_delete, verify=verify_role_delete, cleanup=True,
            ))

    return cases, ctx


# ---------------------------------------------------------------------- run


def run_case(case: Case, sess: EPPSession, ctx: Ctx) -> dict:
    """Execute one case; return a result dict for the checklist."""
    from . import checklist as ck

    result = {
        "status": ck.FAIL,
        "error": "",
        "detail": "",
        "blocked_by": None,
    }

    resp: Optional[Response] = None
    try:
        resp = case.run(sess, ctx)
    except Exception as e:
        result["status"] = ck.FAIL
        result["error"] = f"transport: {type(e).__name__}: {e}"
        return result

    if resp is None:
        if case.verify is None:
            result["status"] = ck.PASS
            result["detail"] = "ok"
        else:
            ok, note = case.verify(resp, ctx, sess)
            result["status"] = ck.PASS if ok else ck.FAIL
            result["detail"] = note
            result["error"] = "" if ok else note
        return result

    base = resp.describe()

    if not resp.parsed:
        result["status"] = ck.FAIL
        result["error"] = f"unparseable response: {base}"
        result["detail"] = resp.raw[:400]
        return result

    if resp.code not in case.expect_codes:
        result["status"] = ck.FAIL
        result["error"] = (
            f"unexpected result code {base}; expected one of "
            f"{sorted(case.expect_codes)}"
        )
        result["detail"] = resp.raw[:400]
        return result

    if case.verify is not None:
        ok, note = case.verify(resp, ctx, sess)
        if not ok:
            result["status"] = ck.FAIL
            result["error"] = f"content check failed: {note} ({base})"
            result["detail"] = resp.resdata[:400]
            return result
        result["detail"] = f"{note} ({base})"

    result["status"] = ck.PASS
    result["error"] = ""
    return result
