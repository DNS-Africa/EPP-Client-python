"""Runner for the RyCE .wien EPP test suite.

Talks EPP to the DAMSR front door in the k8s dev cluster (namespace
``ryce-dev``) and exercises the full chain:

    this suite (EPP client) -> DAMSR -> rEngin -> RyCE OTE (.wien)

Per-zone policy differences are carried by the zone profile in :mod:`.zones`.
The suite is a single-zone runner (``.wien`` / RyCE OTE).

Usage (from ``testing/RyCE``):

    python3 -m suite
    python3 -m suite --phase dnssec
    python3 -m suite --only b-login,s-secdns-add,s-secdns-info --keep -v
    python3 -m suite --env testing/RyCE/.env --out testing/RyCE/checklists

Every case is recorded in the persistent checklist
(``checklists/checklist.json`` + ``CHECKLIST.md``) as it runs.
Exit code 0 when every executed case passed, 1 otherwise.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone

from . import checklist as ck
from . import zones as zones_mod
from .cases import PHASE_DNSSEC, build_cases, run_case
from .epp import CT_NS, DOM_NS, EPPSession, SECDNS_NS, build_ssl_context, load_env, login_xml

REQUIRED_KEYS = ("EPP_HOST", "EPP_PORT", "EPP_USER", "EPP_PASSWORD")

CONNECT_CASE = {"basic": "b-connect", "secdns": "s-connect"}

# Per-session login parameters, used when a session must be re-opened
# (e.g. the registry killed it, or it went stale while idle).
SESSION_LOGINS = {
    "basic": ([DOM_NS, CT_NS], ()),
    "basic-poll": ([DOM_NS, CT_NS], ()),
    "secdns": ([DOM_NS], (SECDNS_NS,)),
}


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _root_blocker(checklist, case_id):
    """Walk a blocked case's ``blocked_by`` chain to the root cause id."""
    root = case_id
    guard = 0
    while guard < 10:
        entry = checklist.state["tests"].get(root, {})
        if entry.get("status") == ck.BLOCKED and entry.get("blocked_by"):
            root = entry["blocked_by"]
            guard += 1
        else:
            break
    return root


def _resolve_blocker(checklist, case):
    """First unmet prerequisite of *case*, reduced to its root cause.

    A prerequisite blocks when its status is FAIL, or BLOCKED (chained to a
    FAIL root). PENDING/SKIPPED/PASS do not block.
    """
    for req in case.requires:
        entry = checklist.state["tests"].get(req, {})
        status = entry.get("status")
        if status == ck.FAIL:
            return req
        if status == ck.BLOCKED:
            root = _root_blocker(checklist, req)
            return root if root != req else req
    return None


def run_zone(zone, cfg, args, out_dir):
    """Run one zone's case list, updating its checklist; return summary counts."""
    host = cfg["EPP_HOST"]
    port = int(cfg.get("EPP_PORT", "3121"))
    timeout = int(cfg.get("EPP_TIMEOUT", "45"))
    os.makedirs(out_dir, exist_ok=True)

    all_cases, ctx = build_cases(cfg, zone)
    checklist = ck.Checklist(
        json_path=os.path.join(out_dir, "checklist.json"),
        md_path=os.path.join(out_dir, "CHECKLIST.md"),
        target=f"{host}:{port} (k8s ns ryce-dev, {zone.registry})",
        registrar=cfg["EPP_USER"],
        title=zone.tld,
    )

    # Select the cases for this run.
    selected = all_cases
    if args.phase != "all":
        selected = [c for c in all_cases if c.phase == args.phase]
    if args.only:
        wanted = {x.strip() for x in args.only.split(",") if x.strip()}
        selected = [c for c in selected if c.id in wanted]
    if args.keep:
        selected = [c for c in selected if not c.cleanup]

    # Register every case so the checklist always shows the full set.
    for case in all_cases:
        checklist.register(case.id, case.name, case.phase)

    print(f"\n=== zone {zone.key} ({zone.registry})  target {host}:{port}  "
          f"registrar {cfg['EPP_USER']}")
    print(f"domain={ctx.domain}  dnssec_domain={ctx.domain_ds}  "
          f"contact={ctx.contact}  roles={ctx.role_handles}")
    print(f"running {len(selected)}/{len(all_cases)} cases "
          f"(phase={args.phase}, keep={args.keep})\n")

    ssl_ctx = build_ssl_context(cfg)

    sessions: dict = {}
    run_ts = _utcnow()

    def open_session(name):
        sess = EPPSession(host, port, timeout=timeout, ssl_ctx=ssl_ctx)
        sessions[name] = sess
        print(f"  [session:{name}] connected "
              f"(TLS {sess.sock.version()})")
        return sess

    for case in selected:
        # 1. prerequisites
        blocker = _resolve_blocker(checklist, case)
        if blocker:
            entry = checklist.state["tests"].get(blocker, {})
            checklist.record(case.id, ck.BLOCKED,
                             error=f"blocked by {blocker}: "
                                   f"{(entry.get('error') or entry.get('detail') or 'no detail')[:200]}",
                             detail=f"prerequisite {blocker} not PASS",
                             blocked_by=blocker)
            checklist.save()
            print(f"[BLOCKED ] {case.id:28s} blocked by {blocker}")
            continue

        # 2. session (connect) - the connect case itself validates the greeting
        try:
            if case.session not in sessions:
                sess = open_session(case.session)
            else:
                sess = sessions[case.session]
        except Exception as e:
            checklist.record(case.id, ck.FAIL,
                             error=f"TLS connect failed: {e}")
            checklist.save()
            print(f"[FAIL    ] {case.id:28s} connect: {e}")
            sessions[case.session] = "dead"
            continue

        sess = sessions[case.session]
        if sess == "dead" or getattr(sess, "dead", False):
            reason = getattr(sess, "dead_reason", "") if sess != "dead" else "session lost"
            recovered = False
            if case.cleanup:
                # Best-effort recovery: re-open and re-login so the cleanup
                # still runs even though the registry killed the session.
                svcs, exts = SESSION_LOGINS.get(case.session, ([DOM_NS, CT_NS], ()))
                try:
                    fresh = EPPSession(host, port, timeout=timeout, ssl_ctx=ssl_ctx)
                    lr = fresh.request(
                        login_xml(cfg["EPP_USER"], cfg["EPP_PASSWORD"], svcs, exts),
                        f"login (recovery {case.session})",
                    )
                    if lr.ok:
                        sessions[case.session] = fresh
                        sess = fresh
                        recovered = True
                        print(f"  [session:{case.session}] recovered for "
                              f"cleanup case {case.id}")
                    else:
                        reason = f"recovery login rejected: {lr.describe()}"
                except Exception as e:  # noqa: BLE001
                    reason = f"recovery failed: {type(e).__name__}: {e}"
            if not recovered:
                checklist.record(case.id, ck.BLOCKED,
                                 error=f"session {case.session} unusable: {reason}",
                                 detail="EPP session lost",
                                 blocked_by=CONNECT_CASE.get(case.session, case.session))
                checklist.save()
                print(f"[BLOCKED ] {case.id:28s} session {case.session} lost")
                continue

        # 3. secDNS gating: when the zone's OTE does not advertise secDNS-1.1
        # in the greeting, the DNSSEC phase cannot be exercised; record the
        # cases as SKIPPED (not FAILED) so the checklist stays clean.
        if case.phase == PHASE_DNSSEC and case.id != "s-connect":
            if not isinstance(sess, EPPSession):
                checklist.record(case.id, ck.BLOCKED,
                                 error="secDNS session lost",
                                 detail="EPP session lost",
                                 blocked_by=CONNECT_CASE.get(case.session, case.session))
                checklist.save()
                print(f"[BLOCKED ] {case.id:28s} secDNS session lost")
                continue
            svcs, exts = sess.greeting_services()
            if SECDNS_NS not in exts:
                checklist.record(case.id, ck.SKIPPED,
                                 error=(f"secDNS-1.1 not advertised in the "
                                        f"{zone.registry} greeting"),
                                 detail="DNSSEC phase not supported by this zone's OTE")
                checklist.save()
                print(f"[SKIP    ] {case.id:28s} secDNS-1.1 not advertised")
                continue

        # 4. execute
        if args.verbose:
            print(f"---- {case.id} : {case.name}")
        # "dead" sentinel in the sessions dict is not an EPPSession.
        if not isinstance(sess, EPPSession):
            checklist.record(case.id, ck.BLOCKED,
                             error="session unavailable",
                             detail="EPP session lost",
                             blocked_by=CONNECT_CASE.get(case.session, case.session))
            checklist.save()
            print(f"[BLOCKED ] {case.id:28s} session lost")
            continue
        started = time.monotonic()
        try:
            result = run_case(case, sess, ctx)
        except Exception as e:  # noqa: BLE001 - record anything unexpected
            result = {
                "status": ck.FAIL,
                "error": f"internal: {type(e).__name__}: {e}",
                "detail": "", "blocked_by": None,
            }
        dur_ms = int((time.monotonic() - started) * 1000)

        # 4.5 transport recovery: if the case's request itself lost the
        # session (OTE drops idle connections, or crashes on an unhandled
        # command), re-open the session, re-login and retry the case once -
        # as a traditional EPP client would reconnect. OTE commands that
        # deterministically kill the connection fail the retry too and keep
        # their FAIL status.
        if (result.get("status") == ck.FAIL
                and str(result.get("error", "")).startswith("transport:")
                and getattr(sess, "dead", False)
                and case.session in SESSION_LOGINS):
            try:
                fresh = EPPSession(host, port, timeout=timeout, ssl_ctx=ssl_ctx)
                svcs, exts = SESSION_LOGINS.get(case.session, ([DOM_NS, CT_NS], ()))
                lr = fresh.request(
                    login_xml(cfg["EPP_USER"], cfg["EPP_PASSWORD"], svcs, exts),
                    f"login (recovery {case.session})",
                )
                if lr.ok:
                    sessions[case.session] = fresh
                    sess = fresh
                    print(f"  [session:{case.session}] re-opened; retrying {case.id}")
                    try:
                        r2 = run_case(case, fresh, ctx)
                    except Exception:  # noqa: BLE001
                        r2 = None
                    if r2 is not None and r2["status"] == ck.PASS:
                        result = r2
                        result["detail"] = (
                            f"(after reconnect retry) {result.get('detail', '')}".strip()
                        )
            except Exception:  # noqa: BLE001 - recovery is best-effort
                pass

        status = result["status"]
        checklist.record(case.id, status,
                         error=result.get("error", ""),
                         detail=result.get("detail", ""),
                         blocked_by=result.get("blocked_by"))
        checklist.save()

        tag = {"PASS": "PASS    ", "FAIL": "FAIL    ", "BLOCKED": "BLOCKED ",
               "SKIPPED": "SKIP    "}[status]
        # On failure, prefer the concise error over the raw-XML detail.
        extra = (result.get('error') or result.get('detail') or "") \
            if status != ck.PASS else (result.get('detail') or "")
        extra = " ".join(extra.split())  # keep XML snippets on one line
        print(f"[{tag}] {case.id:28s} ({dur_ms:>5d} ms)  {extra[:160]}")

        # session went dead mid-run? note it so subsequent cases block
        if getattr(sess, "dead", False):
            sessions[case.session] = "dead"

    # 5. summary
    counts = checklist.summary()
    total = sum(counts.values())
    print(f"zone {zone.key} finished {run_ts}: {counts.get(ck.PASS, 0)} PASS, "
          f"{counts.get(ck.FAIL, 0)} FAIL, "
          f"{counts.get(ck.BLOCKED, 0)} BLOCKED, "
          f"{counts.get(ck.SKIPPED, 0)} SKIPPED, "
          f"{counts.get('PENDING', 0)} pending (of {total})")

    report = checklist.blocker_report()
    if report:
        print(f"zone {zone.key} CURRENTLY BLOCKING:")
        for i, (cid, entry, deps) in enumerate(report, 1):
            err = (entry.get("error") or entry.get("detail") or "no detail")[:200]
            print(f"  {i}. {cid} — {err}")
            if deps:
                print(f"     blocks {len(deps)} test(s): {', '.join(deps)}")
    else:
        print(f"zone {zone.key} CURRENTLY BLOCKING: none")

    print(f"checklist: {checklist.md_path}")
    print(f"state:     {checklist.json_path}")

    return counts


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="End-to-end EPP test suite for the .wien zone "
                    "(DAMSR -> rEngin -> RyCE OTE)"
    )
    default_env = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
    )
    default_checklists = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checklists"
    )
    ap.add_argument("--env", default=default_env,
                    help="env file with credentials/defaults [%default]")
    ap.add_argument("--out", default=default_checklists,
                    help="checklist directory [%(default)s]")
    ap.add_argument("--phase", choices=("all", "basic", "dnssec"), default="all",
                    help="restrict the run to one phase [%(default)s]")
    ap.add_argument("--only", default="",
                    help="comma-separated case ids to run; all others keep "
                         "their previous status")
    ap.add_argument("--keep", action="store_true",
                    help="skip cleanup cases (leave created objects in place)")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="print every request/response XML pair")
    args = ap.parse_args(argv)

    cfg = load_env(args.env)
    missing = [k for k in REQUIRED_KEYS if not cfg.get(k)]
    if missing:
        print(f"error: missing required config key(s) in {args.env}: "
              f"{', '.join(missing)}", file=sys.stderr)
        return 2

    zone = zones_mod.get_zone("wien")
    counts = run_zone(zone, cfg, args, args.out)
    return 0 if (counts.get(ck.FAIL, 0) == 0 and counts.get(ck.BLOCKED, 0) == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
