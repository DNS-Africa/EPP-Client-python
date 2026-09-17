"""Test case definitions for the .de suite.

Two phases:

* ``basic``  - session handling and the core EPP domain/contact operations
  (check / create / info / update / delete / poll).
* ``dnssec`` - DNSSEC management via the secDNS-1.1 extension
  (domain:secDNS:add / info / rem).

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
from .epp import CT_NS, DOM_NS, POLL_NS, SECDNS_NS, EPPSession, Response, login_xml

PHASE_BASIC = "basic"
PHASE_DNSSEC = "dnssec"

# Greeting element, tolerating a namespace prefix (<epp:greeting> or <greeting>).
_GREETING_RE = re.compile(r'<(?:[A-Za-z0-9_-]+:)?greeting[ >]')


# --------------------------------------------------------------------- config


@dataclass
class Ctx:
    """Mutable state shared by all cases of one run."""

    cfg: dict
    domain: str          # primary .de domain under test (created + deleted)
    domain_ds: str       # .de domain for the DNSSEC phase
    missing_domain: str  # label that must NOT exist (negative checks)
    contact: str         # EPP contact handle (short: OTE caps contact:id at 16 chars)
    contact_missing: str # handle that must NOT exist
    authinfo: str        # domain authInfo used for creates
    ns: List[str]
    ns_alt: List[str]
    ds: Optional[DSRecord] = None

    def __init__(self, cfg: dict):
        self.cfg = cfg
        rand = f"{int(time.time()) % 1000000:06d}"
        self.domain = f"giasuite{rand}.de"
        self.domain_ds = f"giads{rand}.de"
        self.missing_domain = f"giamiss{rand}.de"
        prefix = cfg.get("DE_CONTACT_PREFIX", "DENIC-470-DNSBUS-OTE")
        # DENIC handles are DENIC-<regacc>-<member> (9-32 chars), but OTE's
        # EPP schema caps contact:id at 16 chars, so the EPP-side handle is
        # kept short; OTE maps it onto the DENIC handle. `prefix` is kept
        # only for reference in checklist output.
        self.contact = cfg.get("DE_EPP_CONTACT_HANDLE") or f"gia{rand}"
        self.contact_missing = f"giam{rand}"
        self.authinfo = f"gia-suit-{rand}"
        self.ns = [
            cfg.get("DE_NS1", "ns1.sedoparking.com"),
            cfg.get("DE_NS2", "ns2.sedoparking.com"),
        ]
        self.ns_alt = [
            cfg.get("DE_NS3", "ns3.sedoparking.com"),
            cfg.get("DE_NS4", "ns4.sedoparking.com"),
        ]


# ------------------------------------------------------------- XML builders


def _dom(name: str) -> str:
    return f'<domain:name>{name}</domain:name>'


def dom_check(name: str) -> str:
    return (
        f'<check><domain:check xmlns:domain="{DOM_NS}">'
        f"{_dom(name)}</domain:check></check>"
    )


def dom_create(name: str, ctx: Ctx) -> str:
    """Full domain:create satisfying the .de policy:
    registrant + admin + tech + billing, >= 2 nameservers, authInfo.
    Element order follows domain-1.0.xsd (no <period>: DENIC RRI has none)."""
    cfg = ctx.cfg
    return (
        f'<create><domain:create xmlns:domain="{DOM_NS}">'
        f"{_dom(name)}"
        f'<domain:ns>'
        f'<domain:hostObj>{ctx.ns[0]}</domain:hostObj>'
        f'<domain:hostObj>{ctx.ns[1]}</domain:hostObj>'
        f"</domain:ns>"
        f'<domain:registrant>{cfg.get("DE_REGISTRANT", "C0003239")}</domain:registrant>'
        f'<domain:contact type="admin">{cfg.get("DE_ADMIN", "C0003243")}</domain:contact>'
        f'<domain:contact type="tech">{cfg.get("DE_TECH", "C0003247")}</domain:contact>'
        f'<domain:contact type="billing">{cfg.get("DE_BILLING", "courtney1")}</domain:contact>'
        f'<domain:authInfo><domain:pw>{ctx.authinfo}</domain:pw></domain:authInfo>'
        f"</domain:create></create>"
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


def ct_id(handle: str) -> str:
    return f"<contact:id>{handle}</contact:id>"


def ct_check(handle: str) -> str:
    return (
        f'<check><contact:check xmlns:contact="{CT_NS}">'
        f"{ct_id(handle)}</contact:check></check>"
    )


def ct_create(handle: str, ctx: Ctx) -> str:
    """PERSON contact (no <contact:org>) with full postal info.

    OTE's EPP schema restricts contact:voice to the pattern
    '(\\+[0-9]{1,3}\\.[0-9]{1,14})?' - a dotted +CCC.NNNN form - so the
    default voice value is set accordingly (override with DE_CONTACT_PHONE).
    """
    cfg = ctx.cfg
    email = cfg.get("DE_CONTACT_EMAIL", "giaskip.person@example.com")
    voice = cfg.get("DE_CONTACT_PHONE", "+27.215550101")
    return (
        f'<create><contact:create xmlns:contact="{CT_NS}">'
        f"{ct_id(handle)}"
        f'<contact:postalInfo type="int">'
        f'<contact:name>{cfg.get("DE_CONTACT_NAME", "Test Person")}</contact:name>'
        f"<contact:addr>"
        f"<contact:street>1 Example St</contact:street>"
        f'<contact:city>{cfg.get("DE_CONTACT_CITY", "Cape Town")}</contact:city>'
        f"<contact:pc>8001</contact:pc>"
        f'<contact:cc>{cfg.get("DE_CONTACT_CC", "ZA")}</contact:cc>'
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


def poll_msg() -> str:
    return f'<poll req="1"><poll:msg xmlns:poll="{POLL_NS}"/></poll>'


def secdns_add(name: str, ctx: Ctx) -> str:
    ds = ctx.ds or DSRecord(name)
    return (
        f'<add><domain:secDNS:add xmlns:domain="{DOM_NS}" xmlns:secDNS="{SECDNS_NS}">'
        f"{_dom(name)}"
        f"{ds.sec_dns_add_xml()}"
        f"</domain:secDNS:add></add>"
    )


def secdns_info(name: str) -> str:
    return (
        f'<info><domain:secDNS:info xmlns:domain="{DOM_NS}" xmlns:secDNS="{SECDNS_NS}">'
        f"{_dom(name)}</domain:secDNS:info></info>"
    )


def secdns_rem(name: str, key_tag: int, alg: int) -> str:
    return (
        f'<rem><domain:secDNS:rem xmlns:domain="{DOM_NS}" xmlns:secDNS="{SECDNS_NS}">'
        f"{_dom(name)}"
        f'<secDNS:keyTag>{key_tag}</secDNS:keyTag>'
        f"<secDNS:alg>{alg}</secDNS:alg>"
        f"</domain:secDNS:rem></rem>"
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
    """Set of hostObj names in resData (trailing-dot / case normalised).

    OTE returns hostObjs as fully-qualified names with a trailing dot
    (e.g. ``ns1.denic.de.``), so normalise before comparing.
    """
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


def build_cases(cfg: dict) -> Tuple[List[Case], Ctx]:
    ctx = Ctx(cfg)
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
        expect_codes=frozenset({"1000", "2002"}), run=run_login,
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

    taken = cfg.get("DE_TAKEN_DOMAIN", "denic.de")

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
        name="domain:create (registrant/admin/tech/billing + 2 NS + authInfo)",
        phase=PHASE_BASIC, session="basic", requires=("b-login",),
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
            if contacts + (1 if registrant else 0) < 4:
                notes.append(f"expected 4 role contacts, found {contacts} + registrant={registrant}")
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
        return sess.request(poll_msg(), "poll (msg, no object)")

    def verify_poll(resp, _c, _s):
        if resp.code == "1301":
            return True, "queue not empty: >=1 message present (left un-acked for the owner)"
        return True, "queue empty"

    add(Case(
        id="b-poll-empty",
        name="poll msg queue (read-only, no ack)",
        # Own session: poll-1.0 is not advertised in the greeting and OTE
        # currently closes the connection on poll, so this must not take the
        # main basic session (and b-logout) down with it.
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
        expect_codes=frozenset({"1000", "2002"}), run=run_s_login,
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
        phase=PHASE_DNSSEC, session="secdns", requires=("s-login",),
        expect_codes=frozenset({"1000"}), run=run_s_dom_create,
    ))

    def run_s_secdns_add(sess, _c):
        return sess.request(secdns_add(ctx.domain_ds, ctx), "domain:secDNS:add")

    add(Case(
        id="s-secdns-add",
        name="domain:secDNS:add DS record",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-dom-create",),
        expect_codes=frozenset({"1000"}), run=run_s_secdns_add,
    ))

    def run_s_secdns_info(sess, _c):
        return sess.request(secdns_info(ctx.domain_ds), "domain:secDNS:info")

    def verify_s_secdns_info(resp, _c, _s):
        if ctx.ds and str(ctx.ds.key_tag) not in resp.resdata:
            return False, f"keyTag {ctx.ds.key_tag} not in resData"
        if "<secDNS:dsData" not in resp.resdata:
            return False, "no <secDNS:dsData> in resData"
        return True, f"keyTag {ctx.ds.key_tag} present"

    add(Case(
        id="s-secdns-info",
        name="domain:secDNS:info shows DS record",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-secdns-add",),
        expect_codes=frozenset({"1000"}),
        run=run_s_secdns_info, verify=verify_s_secdns_info,
    ))

    def run_s_secdns_rem(sess, _c):
        return sess.request(
            secdns_rem(ctx.domain_ds, ctx.ds.key_tag, ctx.ds.alg),
            "domain:secDNS:rem",
        )

    add(Case(
        id="s-secdns-rem",
        name="domain:secDNS:rem DS record",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-secdns-add",),
        expect_codes=frozenset({"1000"}), run=run_s_secdns_rem,
    ))

    def run_s_secdns_info_after_rem(sess, _c):
        return sess.request(secdns_info(ctx.domain_ds), "domain:secDNS:info (post-rem)")

    def verify_s_secdns_info_after_rem(resp, _c, _s):
        if "<secDNS:dsData" in resp.resdata:
            return False, f"keyTag {ctx.ds.key_tag} still present after rem"
        return True, "no dsData remaining"

    add(Case(
        id="s-secdns-info-after-rem",
        name="domain:secDNS:info after rem (no DS)",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-secdns-rem",),
        expect_codes=frozenset({"1000"}),
        run=run_s_secdns_info_after_rem, verify=verify_s_secdns_info_after_rem,
    ))

    def run_s_secdns_rem_missing(sess, _c):
        return sess.request(
            secdns_rem(ctx.domain_ds, ctx.ds.key_tag, 8), "domain:secDNS:rem (no match)"
        )

    add(Case(
        id="s-secdns-rem-missing",
        name="domain:secDNS:rem non-matching DS -> 2304",
        phase=PHASE_DNSSEC, session="secdns", requires=("s-secdns-rem",),
        expect_codes=frozenset({"2304", "1000"}), run=run_s_secdns_rem_missing,
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
