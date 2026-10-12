"""Test case definitions for the multi-zone EPP suite (.de / .com / .africa).

Cases are built per zone profile (see :mod:`.zones`); the zone drives the
test-domain suffix, the contact roles a domain:create must carry, and where
role contact handles come from (pre-mapped registry handles for .de, contacts
created in-suite for .com / .africa).

Two phases:

* ``basic``  - session handling and the core EPP domain/contact operations
  (check / create / info / update / delete / poll).
* ``dnssec`` - DNSSEC management via the secDNS-1.1 extension (RFC 5910):
  DS add / rem as a ``<secDNS:update>`` extension on ``domain:update``, and
  the ``<secDNS:infData>`` extension on the ``domain:info`` response.

Each case declares which other cases it requires; the runner blocks a case
(instead of running it) when a requirement did not pass, and the checklist
records which test is currently blocking which.

Cases are written to be self-healing on re-runs: if a previous crashed run
left an object behind (create answers "object exists"), the cleanup is
retried and the create is attempted again.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from .ds import DSRecord
from .epp import CT_NS, DOM_NS, RGP_NS, SECDNS_NS, EPPSession, Response, login_xml
from .zones import ROLE_SHORT, Zone

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
    contact: str         # EPP contact handle (short: OTE caps contact:id at 16 chars)
    contact_missing: str # handle that must NOT exist
    authinfo: str        # domain authInfo used for creates
    ns: List[str]
    ns_alt: List[str]
    voice: str
    role_handles: dict   # role -> contact handle used in domain:create
    ds: Optional[DSRecord] = None

    def __init__(self, cfg: dict, zone: Zone):
        self.cfg = cfg
        self.zone = zone
        p = zone.env_prefix
        rand = f"{int(time.time()) % 1000000:06d}"
        self.domain = f"giasuite{rand}{zone.tld}"
        self.domain_ds = f"giads{rand}{zone.tld}"
        self.missing_domain = f"giamiss{rand}{zone.tld}"
        # DENIC handles are DENIC-<regacc>-<member> (9-32 chars), but OTE's
        # EPP schema caps contact:id at 16 chars, so the EPP-side handle is
        # kept short; OTE maps it onto the DENIC handle.
        self.contact = cfg.get(f"{p}_EPP_CONTACT_HANDLE") or f"gia{rand}"
        self.contact_missing = f"giam{rand}"
        self.authinfo = f"gia-suit-{rand}"
        self.ns = [
            cfg.get(f"{p}_NS1", "ns1.sedoparking.com"),
            cfg.get(f"{p}_NS2", "ns2.sedoparking.com"),
        ]
        self.ns_alt = [
            cfg.get(f"{p}_NS3", "ns3.sedoparking.com"),
            cfg.get(f"{p}_NS4", "ns4.sedoparking.com"),
        ]
        self.voice = cfg.get(f"{p}_CONTACT_PHONE") or zone.phone_default
        self.role_handles = {}
        for role in zone.required_roles:
            if zone.contact_source == "env":
                # Pre-mapped registry handles (zone_contact mappings).
                self.role_handles[role] = cfg.get(
                    zone.role_env_key(role), zone.role_defaults.get(role)
                )
            else:
                # Suite-created contacts: short EPP handles (< 16 chars).
                self.role_handles[role] = f"gia-{ROLE_SHORT[role]}-{rand}"


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
    authInfo? (no <period>: DENIC RRI has none). The OTE schema validates
    this order strictly (ns after the contacts -> 2001).
    """
    zone = ctx.zone
    parts = [f"<domain:name>{name}</domain:name>"]
    parts.append(
        f'<domain:ns>'
        f'<domain:hostObj>{ctx.ns[0]}</domain:hostObj>'
        f'<domain:hostObj>{ctx.ns[1]}</domain:hostObj>'
        f"</domain:ns>"
    )
    if "registrant" in zone.required_roles:
        parts.append(f'<domain:registrant>{ctx.role_handles["registrant"]}</domain:registrant>')
    for role in ("admin", "tech", "billing"):
        if role in zone.required_roles:
            parts.append(f'<domain:contact type="{role}">{ctx.role_handles[role]}</domain:contact>')
    parts.append(f'<domain:authInfo><domain:pw>{ctx.authinfo}</domain:pw></domain:authInfo>')
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
    """Standard EPP domain:update: <domain:add>/<domain:rem> wrap the NS list.
    OTE validates element order as name, add?, rem?, chg? (empirically: a
    <domain:rem> before <domain:add> is rejected with 2001)."""
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


def _dom_update(name: str, add: str = "", rem: str = "", chg: str = "", ext: str = "") -> str:
    """RFC 5731 domain:update; add/rem/chg are the inner XML of each block."""
    return (
        f'<update><domain:update xmlns:domain="{DOM_NS}">'
        f"{_dom(name)}"
        + (f"<domain:add>{add}</domain:add>" if add else "")
        + (f"<domain:rem>{rem}</domain:rem>" if rem else "")
        + (f"<domain:chg>{chg}</domain:chg>" if chg else "")
        + "</domain:update></update>"
        + (f"<extension>{ext}</extension>" if ext else "")
    )


def dom_update_ns_attr(name: str, add: List[str], rem: List[str]) -> str:
    """NS change with the RFC 5731 hostAttr model (no host objects), which is
    what a server that does not advertise host-1.0 is expected to accept."""
    attr = lambda ns: "".join(
        f"<domain:hostAttr><domain:hostName>{n}</domain:hostName></domain:hostAttr>" for n in ns)
    return _dom_update(
        name,
        add=f"<domain:ns>{attr(add)}</domain:ns>" if add else "",
        rem=f"<domain:ns>{attr(rem)}</domain:ns>" if rem else "",
    )


def dom_update_contact(name: str, role: str, add: str, rem: str) -> str:
    return _dom_update(
        name,
        add=f'<domain:contact type="{role}">{add}</domain:contact>',
        rem=f'<domain:contact type="{role}">{rem}</domain:contact>',
    )


def dom_update_registrant(name: str, registrant: str) -> str:
    """Holder change (DENIC chholder) as RFC 5731 chg/registrant."""
    return _dom_update(name, chg=f"<domain:registrant>{registrant}</domain:registrant>")


def dom_update_authinfo(name: str, pw: str) -> str:
    return _dom_update(name, chg=f"<domain:authInfo><domain:pw>{pw}</domain:pw></domain:authInfo>")


def dom_renew(name: str, cur_exp: str, years: int = 1) -> str:
    return (
        f'<renew><domain:renew xmlns:domain="{DOM_NS}">'
        f"{_dom(name)}<domain:curExpDate>{cur_exp}</domain:curExpDate>"
        f'<domain:period unit="y">{years}</domain:period>'
        f"</domain:renew></renew>"
    )


def dom_transfer(name: str, op: str, pw: str = "") -> str:
    auth = f"<domain:authInfo><domain:pw>{pw}</domain:pw></domain:authInfo>" if pw else ""
    return (
        f'<transfer op="{op}"><domain:transfer xmlns:domain="{DOM_NS}">'
        f"{_dom(name)}{auth}</domain:transfer></transfer>"
    )


def dom_restore_request(name: str) -> str:
    """RFC 3915 restore request: empty domain:update + rgp:update."""
    return (
        f'<update><domain:update xmlns:domain="{DOM_NS}">'
        f"{_dom(name)}<domain:chg/></domain:update></update>"
        f'<extension><rgp:update xmlns:rgp="{RGP_NS}">'
        f'<rgp:restore op="request"/></rgp:update></extension>'
    )


def ct_id(handle: str) -> str:
    return f"<contact:id>{handle}</contact:id>"


def ct_check(handle: str) -> str:
    return (
        f'<check><contact:check xmlns:contact="{CT_NS}">'
        f"{ct_id(handle)}</contact:check></check>"
    )


def ct_create(handle: str, ctx: Ctx) -> str:
    """PERSON contact (no <contact:org>) with full postal info.

    contact:voice uses the RFC 5733 e164StringType pattern
    '(\\+[0-9]{1,3}\\.[0-9]{1,14})?' (dotted +CCC.NNNN form). Override per
    zone with <PREFIX>_CONTACT_PHONE.
    """
    cfg = ctx.cfg
    p = ctx.zone.env_prefix
    email = cfg.get(f"{p}_CONTACT_EMAIL", "giaskip.person@example.com")
    voice = cfg.get(f"{p}_CONTACT_PHONE") or ctx.zone.phone_default
    city = cfg.get(f"{p}_CONTACT_CITY", "Cape Town")
    cc = cfg.get(f"{p}_CONTACT_CC", "ZA")
    name = cfg.get(f"{p}_CONTACT_NAME", "Test Person")
    return (
        f'<create><contact:create xmlns:contact="{CT_NS}">'
        f"{ct_id(handle)}"
        f'<contact:postalInfo type="int">'
        f"<contact:name>{name}</contact:name>"
        # RFC 5733 addrType order: street*, city, sp?, pc?, cc. The edge
        # schema-validates this and rejects any other order with 2001.
        f"<contact:addr>"
        f"<contact:street>1 Example St</contact:street>"
        f"<contact:city>{city}</contact:city>"
        f"<contact:pc>8001</contact:pc>"
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


def _secdns_data(ds: DSRecord, interface: str) -> str:
    return ds.sec_dns_key_xml() if interface == "key" else ds.sec_dns_add_xml()


def secdns_add(name: str, ds: DSRecord, interface: str = "ds") -> str:
    return _secdns_update(name, f"<secDNS:add>{_secdns_data(ds, interface)}</secDNS:add>")


def secdns_rem(name: str, ds: DSRecord, interface: str = "ds") -> str:
    """Remove one DS/DNSKEY; RFC 5910 identifies it by the full dsData
    (keyTag, alg, digestType, digest) or keyData (flags, protocol, alg, pubKey)."""
    return _secdns_update(name, f"<secDNS:rem>{_secdns_data(ds, interface)}</secDNS:rem>")


def _has_secdns(resp: Response, ds: DSRecord, interface: str) -> bool:
    """True when the domain:info secDNS:infData carries this DS/DNSKEY."""
    if interface == "key":
        return ds.pub_key_b64 in re.sub(r"\s+", "", resp.extension)
    return str(ds.key_tag) in _ds_key_tags(resp)


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
    """Set of nameserver names in resData, hostObj or hostAttr/hostName
    (trailing-dot / case normalised).

    OTE returns hostObjs as fully-qualified names with a trailing dot
    (e.g. ``ns1.denic.de.``), so normalise before comparing.
    """
    vals = re.findall(r'<domain:(?:hostObj|hostName)[^>]*>([^<]*)</domain:(?:hostObj|hostName)>',
                      resp.resdata)
    return {v.rstrip(".").lower() for v in vals}


def _registrant(resp: Response) -> Optional[str]:
    """Registrant handle from domain:infData, RFC form or the
    ``<domain:contact type="registrant">`` deviation."""
    m = re.search(r'<domain:registrant>([^<]*)</domain:registrant>', resp.resdata) or \
        re.search(r'<domain:contact type="registrant">([^<]*)</domain:contact>', resp.resdata)
    return m.group(1).strip() if m else None


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

    # Zones with contact_source == "create" (com, africa) have no pre-mapped
    # registry handles, so the role contacts are created in-suite before the
    # domain:create that references them.
    role_create_ids: List[str] = []
    if zone.contact_source == "create":
        for role in zone.required_roles:
            handle = ctx.role_handles[role]
            role_create_ids.append(f"b-ct-role-create-{role}")

            def run_role_create(sess, _c, _handle=handle, _role=role):
                resp = sess.request(ct_create(_handle, ctx), f"contact:create ({_role})")
                # Self-heal on "object exists" from a previous crashed run.
                if resp.code in ("2101", "2302", "2304", "2306"):
                    sess.request(ct_delete(_handle), f"contact:create-cleanup-delete ({_role})")
                    resp = sess.request(ct_create(_handle, ctx), f"contact:create ({_role}, retry)")
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
        # Self-heal: a previous crashed run may have left this exact label
        # behind (duplicate create -> object-exists error).
        if resp.code in ("2302", "2305"):
            sess.request(dom_delete(ctx.domain), "domain:create-cleanup-delete")
            resp = sess.request(dom_create(ctx.domain, ctx), "domain:create (retry)")
        return resp

    add(Case(
        id="b-dom-create",
        name=f"domain:create ({'/'.join(zone.required_roles)} + 2 NS + authInfo)",
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
        # Hard check: the created domain is actually returned. Field-level
        # gaps are reported as notes - OTE omits NS while the domain is
        # pendingCreate (cf. denic.de, which does return hostObj).
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
                    notes.append("no hostObj yet (expected while pendingCreate; OTE returns NS only once active)")
                else:
                    notes.append(f"DEVIATION: expected >=2 hostObj in info, found {len(ns)}")
            if "<domain:authInfo>" not in rd:
                notes.append("authInfo missing from info")
            contacts = rd.count("<domain:contact type=")
            registrant = "<domain:registrant>" in rd
            expected_roles = len(zone.required_roles)
            if contacts + (1 if registrant else 0) < expected_roles:
                notes.append(f"expected {expected_roles} role contacts, found {contacts} + registrant={registrant}")
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
            dom_update_ns(ctx.domain, add=ctx.ns_alt, rem=ctx.ns), "domain:update (ns swap)"
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
        # If OTE returns no hostObj at all, the read-back cannot confirm the
        # swap - pass with a note instead of a hard fail (the update command
        # itself already returned 1000).
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

    # ------------------------------------------------- registrar onboarding
    # Standard EPP operations a registrar uses day to day, each expecting a
    # clean RFC answer. A FAIL here is something the chain still has to fix
    # before the zone can be onboarded.
    if zone.onboarding:
        roles = ctx.role_handles

        def run_rfc_avail(sess, _c):
            return sess.request(dom_check(ctx.missing_domain), "domain:check (RFC form)")

        def verify_rfc_avail(resp, _c, _s):
            if re.search(r'<domain:name\b[^>]*\bavail="[01]"', resp.resdata):
                return True, "avail is the domain:name/@avail attribute"
            return False, ("RFC 5731 3.1.1: avail must be an attribute of <domain:name>; "
                           f"got {' '.join(resp.resdata.split())[:200]}")

        add(Case(
            id="o-rfc-check-avail",
            name="domain:check response uses domain:name/@avail (RFC 5731)",
            phase=PHASE_BASIC, session="basic", requires=("b-login",),
            expect_codes=frozenset({"1000"}), run=run_rfc_avail, verify=verify_rfc_avail,
        ))

        def run_rfc_info(sess, _c):
            return sess.request(dom_info(ctx.domain), "domain:info (RFC form)")

        def verify_rfc_info(resp, _c, _s):
            problems = []
            if "<domain:registrant>" not in resp.resdata:
                problems.append("no <domain:registrant>")
            if 'type="registrant"' in resp.resdata:
                problems.append('<domain:contact type="registrant"> is not a valid contact type '
                                "(RFC 5731 allows admin/billing/tech)")
            if "<domain:roid>" not in resp.resdata:
                problems.append("no <domain:roid> (mandatory)")
            if not re.search(r'<domain:status\b', resp.resdata):
                problems.append("no <domain:status> (mandatory, at least one)")
            if problems:
                return False, "RFC 5731 infData: " + "; ".join(problems)
            return True, "registrant/roid/status present in RFC form"

        add(Case(
            id="o-rfc-info-fields",
            name="domain:info response has RFC registrant/roid/status",
            phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
            expect_codes=frozenset({"1000"}), run=run_rfc_info, verify=verify_rfc_info,
        ))

        attr_target: dict = {}

        def run_ns_attr(sess, _c):
            cur = _ns_set(sess.request(dom_info(ctx.domain), "domain:info (pre hostAttr)"))
            new = ctx.ns_alt if set(n.lower() for n in ctx.ns) & cur else ctx.ns
            attr_target["add"], attr_target["rem"] = new, sorted(cur)
            return sess.request(dom_update_ns_attr(ctx.domain, new, sorted(cur)),
                                "domain:update (hostAttr NS swap)")

        add(Case(
            id="o-dom-update-ns-attr",
            name="domain:update NS swap with hostAttr (new hosts)",
            phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
            expect_codes=frozenset({"1000"}), run=run_ns_attr,
        ))

        def run_ns_attr_info(sess, _c):
            return sess.request(dom_info(ctx.domain), "domain:info (post hostAttr)")

        def verify_ns_attr_info(resp, _c, _s):
            ns = _ns_set(resp)
            missing = [n for n in attr_target.get("add", []) if n.lower() not in ns]
            stale = [n for n in attr_target.get("rem", []) if n in ns]
            if missing or stale:
                return False, f"NS now {sorted(ns)}; missing {missing}, still present {stale}"
            return True, f"NS now {sorted(ns)}"

        add(Case(
            id="o-dom-info-after-ns-attr",
            name="domain:info shows the hostAttr NS swap",
            phase=PHASE_BASIC, session="basic", requires=("o-dom-update-ns-attr",),
            expect_codes=frozenset({"1000"}), run=run_ns_attr_info, verify=verify_ns_attr_info,
        ))

        def run_contact_swap(sess, _c):
            return sess.request(
                dom_update_contact(ctx.domain, "tech", add=roles["admin"], rem=roles["tech"]),
                "domain:update (tech contact swap)")

        add(Case(
            id="o-dom-update-contact",
            name="domain:update swap tech contact",
            phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
            expect_codes=frozenset({"1000"}), run=run_contact_swap,
        ))

        def run_contact_swap_info(sess, _c):
            return sess.request(dom_info(ctx.domain), "domain:info (post contact swap)")

        def verify_contact_swap_info(resp, _c, _s):
            techs = re.findall(r'<domain:contact type="tech">([^<]*)<', resp.resdata)
            if techs == [roles["admin"]]:
                return True, f"tech contact now {techs}"
            return False, f"tech contact(s) {techs}, expected [{roles['admin']}]"

        add(Case(
            id="o-dom-info-after-contact",
            name="domain:info shows the new tech contact",
            phase=PHASE_BASIC, session="basic", requires=("o-dom-update-contact",),
            expect_codes=frozenset({"1000"}),
            run=run_contact_swap_info, verify=verify_contact_swap_info,
        ))

        new_holder = cfg.get(f"{zone.env_prefix}_ALT_REGISTRANT", roles["admin"])

        def run_chholder(sess, _c):
            return sess.request(dom_update_registrant(ctx.domain, new_holder),
                                "domain:update (chg registrant / chholder)")

        add(Case(
            id="o-dom-chholder",
            name=f"domain:update chg registrant -> {new_holder} (holder change)",
            phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
            expect_codes=frozenset({"1000", "1001"}), run=run_chholder,
        ))

        def run_chholder_info(sess, _c):
            return sess.request(dom_info(ctx.domain), "domain:info (post chholder)")

        def verify_chholder_info(resp, _c, _s):
            got = _registrant(resp)
            if got == new_holder:
                return True, f"registrant now {got}"
            return False, f"registrant {got!r}, expected {new_holder!r}"

        add(Case(
            id="o-dom-info-after-chholder",
            name="domain:info shows the new registrant",
            phase=PHASE_BASIC, session="basic", requires=("o-dom-chholder",),
            expect_codes=frozenset({"1000"}),
            run=run_chholder_info, verify=verify_chholder_info,
        ))

        new_pw = f"{ctx.authinfo}-b"

        def run_authinfo(sess, _c):
            return sess.request(dom_update_authinfo(ctx.domain, new_pw),
                                "domain:update (chg authInfo)")

        add(Case(
            id="o-dom-update-authinfo",
            name="domain:update chg authInfo (transfer code)",
            phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
            expect_codes=frozenset({"1000"}), run=run_authinfo,
        ))

        def run_authinfo_info(sess, _c):
            return sess.request(dom_info(ctx.domain), "domain:info (post authInfo)")

        def verify_authinfo_info(resp, _c, _s):
            if f"<domain:pw>{new_pw}</domain:pw>" in resp.resdata:
                return True, "new authInfo returned to the sponsor"
            m = re.search(r'<domain:pw>([^<]*)</domain:pw>', resp.resdata)
            return False, f"authInfo {m.group(1) if m else None!r}, expected the new value"

        add(Case(
            id="o-dom-info-after-authinfo",
            name="domain:info returns the new authInfo",
            phase=PHASE_BASIC, session="basic", requires=("o-dom-update-authinfo",),
            expect_codes=frozenset({"1000"}),
            run=run_authinfo_info, verify=verify_authinfo_info,
        ))

        def run_renew(sess, _c):
            info = sess.request(dom_info(ctx.domain), "domain:info (pre renew)")
            m = re.search(r'<domain:exDate>(\d{4}-\d{2}-\d{2})', info.resdata)
            if m:
                cur = m.group(1)
            else:
                # infData exDate is optional; fall back to crDate + 1 year.
                c = re.search(r'<domain:crDate>(\d{4})(-\d{2}-\d{2})', info.resdata)
                cur = f"{int(c.group(1)) + 1}{c.group(2)}" if c else time.strftime("%Y-%m-%d")
            return sess.request(dom_renew(ctx.domain, cur), f"domain:renew (curExpDate {cur})")

        add(Case(
            id="o-dom-renew",
            name="domain:renew 1y -> 1000, or a clean 2xxx refusal (not 2400)",
            phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
            # .de renews automatically; a clean policy refusal is acceptable,
            # an internal error is not.
            expect_codes=frozenset({"1000", "1001", "2101", "2105", "2306"}), run=run_renew,
        ))

        def run_transfer_query(sess, _c):
            return sess.request(dom_transfer(ctx.domain, "query"), "domain:transfer op=query")

        add(Case(
            id="o-dom-transfer-query",
            name="domain:transfer query (no transfer pending) -> 1000/2301",
            phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
            expect_codes=frozenset({"1000", "2301"}), run=run_transfer_query,
        ))

        def run_transfer_own(sess, _c):
            return sess.request(dom_transfer(ctx.domain, "request", new_pw),
                                "domain:transfer op=request (own domain)")

        add(Case(
            id="o-dom-transfer-own",
            name="domain:transfer request on own domain -> 2106 (chprov path)",
            phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
            expect_codes=frozenset({"2106", "2201", "2304"}), run=run_transfer_own,
        ))

    def run_dom_delete(sess, _c):
        return sess.request(dom_delete(ctx.domain), "domain:delete")

    add(Case(
        id="b-dom-delete",
        name="domain:delete",
        # Requires only b-dom-create (not the update step) so the domain is
        # always cleaned up, even when b-dom-update-ns fails.
        phase=PHASE_BASIC, session="basic", requires=("b-dom-create",),
        # 1001 = accepted, action pending (DENIC deletes can be async).
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
        # OTE delete of a fresh domain is async (1001, grace-period
        # suspension), so the domain may still show as not-available.
        return True, ("post-delete check: avail=0 - delete still pending "
                      "(async grace-period suspension, expected right after 1001)")

    add(Case(
        id="b-dom-check-after-delete",
        name="domain:check after delete -> avail=1",
        phase=PHASE_BASIC, session="basic", requires=("b-dom-delete",),
        expect_codes=frozenset({"1000"}),
        run=run_dom_check_after_delete, verify=verify_dom_check_after_delete,
    ))

    if zone.onboarding:
        def verify_rgp_greeting(resp, _c, sess):
            _svcs, exts = sess.greeting_services()
            return (RGP_NS in exts,
                    "rgp-1.0 advertised" if RGP_NS in exts
                    else f"rgp-1.0 not in greeting extensions {exts}: registrars cannot restore (RFC 3915)")

        add(Case(
            id="o-rfc-greeting-rgp",
            name="greeting advertises rgp-1.0 (needed for restore)",
            phase=PHASE_BASIC, session="basic", requires=("b-connect",),
            expect_codes=frozenset(), run=lambda _s, _c: None, verify=verify_rgp_greeting,
        ))

        def run_restore(sess, _c):
            # Own session: restore needs rgp-1.0 declared at login.
            if not getattr(sess, "logged_in", False):
                r = sess.request(
                    login_xml(cfg["EPP_USER"], cfg["EPP_PASSWORD"], [DOM_NS, CT_NS], [RGP_NS]),
                    "login (rgp session)",
                )
                sess.logged_in = r.ok
                if not r.ok:
                    return r
            return sess.request(dom_restore_request(ctx.domain), "domain:update rgp:restore request")

        add(Case(
            id="o-dom-restore",
            name="restore the deleted domain (RFC 3915 rgp:restore op=request)",
            phase=PHASE_BASIC, session="basic-rgp", requires=("b-dom-delete",),
            expect_codes=frozenset({"1000", "1001"}), run=run_restore,
        ))

        def run_restore_info(sess, _c):
            return sess.request(dom_info(ctx.domain), "domain:info (post restore)")

        def verify_restore_info(resp, _c, _s):
            st = re.findall(r'<domain:status[^>]*\bs="([A-Za-z]+)"', resp.resdata)
            if "pendingDelete" in st:
                return False, f"still pendingDelete after restore: {st}"
            return True, f"status {st}"

        add(Case(
            id="o-dom-info-after-restore",
            name="domain:info after restore (not pendingDelete)",
            phase=PHASE_BASIC, session="basic-rgp", requires=("o-dom-restore",),
            expect_codes=frozenset({"1000"}), run=run_restore_info, verify=verify_restore_info,
        ))

        def run_delete_final(sess, _c):
            return sess.request(dom_delete(ctx.domain), "domain:delete (after restore)")

        add(Case(
            id="o-dom-delete-final",
            name="domain:delete again after restore (cleanup)",
            phase=PHASE_BASIC, session="basic-rgp", requires=("o-dom-restore",),
            expect_codes=frozenset({"1000", "1001"}), run=run_delete_final, cleanup=True,
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
        # Self-heal on "object exists" (any 2xxx where delete may apply).
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

    new_email = "giaskip.updated@example.com"

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
        # The poll session is isolated; a traditional EPP client authenticates
        # before poll, so log this session in first when it is fresh.
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
        # Own session so a poll failure cannot take the main basic session
        # (and b-logout) down with it.
        phase=PHASE_BASIC, session="basic-poll", requires=("b-login",),
        expect_codes=frozenset({"1300", "1301"}), run=run_poll, verify=verify_poll,
    ))

    def run_logout(sess, _c):
        return sess.request("<logout/>", "logout")

    add(Case(
        id="b-logout",
        name="logout",
        phase=PHASE_BASIC, session="basic", requires=("b-login",),
        # 1500 is the standard logout success code ("ending session").
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
            resp = sess.request(dom_create(ctx.domain_ds, ctx), "domain:create (dnssec, retry)")
        return resp

    add(Case(
        id="s-dom-create",
        name="domain:create for DNSSEC target",
        # Role contacts (com/africa) are created in the basic phase.
        phase=PHASE_DNSSEC, session="secdns", requires=("s-login", *role_create_ids),
        expect_codes=frozenset({"1000"}), run=run_s_dom_create,
    ))

    def run_s_secdns_add(sess, _c):
        return sess.request(secdns_add(ctx.domain_ds, ctx.ds, zone.secdns_interface),
                            f"domain:update +secDNS:add ({zone.secdns_interface}Data)")

    add(Case(
        id="s-secdns-add",
        name="domain:update secDNS:add DS record",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-dom-create",),
        expect_codes=frozenset({"1000"}), run=run_s_secdns_add,
    ))

    def run_s_secdns_info(sess, _c):
        return sess.request(dom_info(ctx.domain_ds), "domain:info (secDNS)")

    def verify_s_secdns_info(resp, _c, _s):
        if "infData" not in resp.extension:
            return False, "no <secDNS:infData> in response <extension>"
        if not _has_secdns(resp, ctx.ds, zone.secdns_interface):
            return False, (f"{zone.secdns_interface}Data (keyTag {ctx.ds.key_tag}) not in "
                           f"secDNS:infData (keyTags {_ds_key_tags(resp)})")
        return True, f"{zone.secdns_interface}Data (keyTag {ctx.ds.key_tag}) present in secDNS:infData"

    add(Case(
        id="s-secdns-info",
        name="domain:info shows DS in secDNS:infData",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-secdns-add",),
        expect_codes=frozenset({"1000"}),
        run=run_s_secdns_info, verify=verify_s_secdns_info,
    ))

    def run_s_secdns_rem(sess, _c):
        return sess.request(secdns_rem(ctx.domain_ds, ctx.ds, zone.secdns_interface),
                            "domain:update +secDNS:rem")

    add(Case(
        id="s-secdns-rem",
        name="domain:update secDNS:rem DS record",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-secdns-add",),
        expect_codes=frozenset({"1000"}), run=run_s_secdns_rem,
    ))

    def run_s_secdns_info_after_rem(sess, _c):
        return sess.request(dom_info(ctx.domain_ds), "domain:info (secDNS, post-rem)")

    def verify_s_secdns_info_after_rem(resp, _c, _s):
        if _has_secdns(resp, ctx.ds, zone.secdns_interface):
            return False, f"keyTag {ctx.ds.key_tag} still in secDNS:infData after rem"
        return True, "DS/DNSKEY no longer in secDNS:infData"

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
            secdns_rem(ctx.domain_ds, DSRecord(ctx.domain_ds), zone.secdns_interface),
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
        # Requires only s-dom-create (not the secDNS chain) so the registry
        # object is cleaned up even when secDNS operations are blocked.
        phase=PHASE_DNSSEC, session="secdns", requires=("s-dom-create",),
        # 1001 = accepted, action pending (DENIC deletes can be async).
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

    # Role contacts are shared by the basic-phase and DNSSEC-phase domains, so
    # they are deleted last, only after both domains are gone.
    if zone.contact_source == "create":
        for role in zone.required_roles:
            handle = ctx.role_handles[role]

            def run_role_delete(sess, _c, _handle=handle, _role=role):
                return sess.request(ct_delete(_handle), f"contact:delete ({_role})")

            def verify_role_delete(resp, _c, _s, _role=role):
                if resp.code == "2305":
                    return True, (
                        f"{_role} contact still associated with the "
                        f"pending-delete domain (OTE grace-period suspension); "
                        f"association releases when the domain delete completes"
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
        "denic_codes": [],
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
        # No EPP command was sent (connect-only case): judge via verify.
        if case.verify is None:
            result["status"] = ck.PASS
            result["detail"] = "ok"
        else:
            ok, note = case.verify(resp, ctx, sess)
            result["status"] = ck.PASS if ok else ck.FAIL
            result["detail"] = note
            result["error"] = "" if ok else note
        return result

    result["denic_codes"] = resp.denic_codes
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


def EXTRA_REQUESTS(ctx: Ctx, ds: DSRecord) -> dict:
    """Additional request builders, for offline XSD validation of the suite."""
    d = ctx.domain
    return {
        "dom_update_ns_attr": dom_update_ns_attr(d, ctx.ns_alt, ctx.ns),
        "dom_update_contact": dom_update_contact(d, "tech", "ab1", "ab2"),
        "dom_update_registrant": dom_update_registrant(d, "ab1"),
        "dom_update_authinfo": dom_update_authinfo(d, "pw-123456"),
        "dom_renew": dom_renew(d, "2027-01-01"),
        "dom_transfer_query": dom_transfer(d, "query"),
        "dom_transfer_request": dom_transfer(d, "request", "pw-123456"),
        "dom_restore_request": dom_restore_request(d),
        "secdns_add_key": secdns_add(ctx.domain_ds, ds, "key"),
        "secdns_rem_key": secdns_rem(ctx.domain_ds, ds, "key"),
    }
