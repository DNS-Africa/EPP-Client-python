"""Persistent checklist for the .de test suite.

State is kept in ``checklist.json`` (machine-readable) and rendered to
``CHECKLIST.md`` (human-readable) after every test. The markdown file is the
"live" checklist: it records which tests pass, fail or are blocked, the error
currently blocking each blocked test, and which failure is the current
blocker for the rest of the run.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

PASS = "PASS"
FAIL = "FAIL"
BLOCKED = "BLOCKED"

_SYMBOL = {PASS: "PASS", FAIL: "FAIL", BLOCKED: "BLOCKED"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


class Checklist:
    def __init__(self, json_path, md_path, target, registrar):
        self.json_path = json_path
        self.md_path = md_path
        self.target = target
        self.registrar = registrar
        self.state = {
            "meta": {
                "target": target,
                "registrar": registrar,
                "first_run": None,
                "last_run": None,
            },
            "tests": {},
            "runs": [],  # last N summaries, oldest first
        }
        self._load()

    # ------------------------------------------------------------------ load

    def _load(self):
        if not os.path.exists(self.json_path):
            return
        try:
            with open(self.json_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, OSError):
            return
        if not isinstance(data, dict) or "tests" not in data:
            return
        # Restore persistent state. The current run's target/registrar win
        # over stale meta, and run_ts is intentionally NOT loaded: it is
        # per-process, so each process run adds exactly one history entry.
        self.state["tests"] = data.get("tests", {})
        self.state["runs"] = data.get("runs", [])
        old_meta = data.get("meta") or {}
        self.state["meta"]["first_run"] = old_meta.get("first_run")

    # ---------------------------------------------------------------- record

    def register(self, case_id, name, phase):
        """Ensure a test entry exists (used to pre-seed BLOCKED rows)."""
        t = self.state["tests"].setdefault(
            case_id,
            {
                "name": name,
                "phase": phase,
                "status": None,
                "previous": None,
                "error": "",
                "denic_codes": [],
                "detail": "",
                "blocked_by": None,
                "last_run": None,
            },
        )
        t["name"] = name
        t["phase"] = phase
        return t

    def record(self, case_id, status, error="", denic_codes=None, detail="",
               blocked_by=None):
        prev = self.state["tests"].get(case_id, {}).get("status")
        entry = self.state["tests"].setdefault(case_id, {"phase": "?"})
        entry["status"] = status
        entry["previous"] = prev
        entry["error"] = error
        entry["denic_codes"] = denic_codes or []
        entry["detail"] = detail
        entry["blocked_by"] = blocked_by
        entry["last_run"] = _now()
        return entry

    # ------------------------------------------------------------- reporting

    def blocker_report(self):
        """Tests that are FAILED/BLOCKED and currently block downstream tests.

        Returns a list of (case_id, entry, [blocked case ids]) sorted by case
        id. A test counts as a blocker when at least one other test records it
        as its ``blocked_by`` (following the chain to the root failure).
        """
        tests = self.state["tests"]
        blocked_by_map = {}
        for cid, t in tests.items():
            if t.get("status") == BLOCKED and t.get("blocked_by"):
                # Walk the chain to the root blocker.
                root = t["blocked_by"]
                guard = 0
                while guard < 10 and tests.get(root, {}).get("status") == BLOCKED \
                        and tests.get(root, {}).get("blocked_by"):
                    root = tests[root]["blocked_by"]
                    guard += 1
                blocked_by_map.setdefault(root, []).append(cid)
        report = []
        for cid, deps in sorted(blocked_by_map.items()):
            entry = tests.get(cid)
            if entry is not None and entry.get("status") in (FAIL, BLOCKED):
                report.append((cid, entry, sorted(set(deps))))
        return report

    def summary(self):
        counts = {PASS: 0, FAIL: 0, BLOCKED: 0, "PENDING": 0}
        for t in self.state["tests"].values():
            counts[t.get("status") or "PENDING"] = counts.get(
                t.get("status") or "PENDING", 0) + 1
        return counts

    # ----------------------------------------------------------------- save

    def save(self):
        meta = self.state["meta"]
        now = _now()
        if meta.get("first_run") is None:
            meta["first_run"] = now
        # One history entry per process run: reuse the run-start timestamp so
        # repeated saves within the same run update the last entry in place.
        if not meta.get("run_ts"):
            meta["run_ts"] = now
        meta["last_run"] = now
        entry = {"ts": meta["run_ts"], **self._summary_counts()}
        runs = self.state["runs"]
        if runs and runs[-1]["ts"] == meta["run_ts"]:
            runs[-1] = entry
        else:
            runs.append(entry)
        self.state["runs"] = runs[-20:]

        with open(self.json_path, "w", encoding="utf-8") as fh:
            json.dump(self.state, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        with open(self.md_path, "w", encoding="utf-8") as fh:
            fh.write(self._render())

    def _summary_counts(self):
        c = self.summary()
        total = sum(c.values())
        return {
            "pass": c.get(PASS, 0),
            "fail": c.get(FAIL, 0),
            "blocked": c.get(BLOCKED, 0),
            "pending": c.get("PENDING", 0),
            "total": total,
        }

    def _render(self):
        counts = self._summary_counts()
        lines = []
        lines.append("# .de zone test checklist")
        lines.append("")
        lines.append(f"- **Target:** {self.target}  ")
        lines.append(f"- **Registrar:** {self.registrar}  ")
        lines.append(f"- **Last run:** {self.state['meta']['last_run']}  ")
        lines.append(
            f"- **Result:** {counts['pass']} passed, {counts['fail']} failed, "
            f"{counts['blocked']} blocked, {counts['pending']} pending "
            f"(of {counts['total']})"
        )
        lines.append("")
        lines.append("## Currently blocking")
        lines.append("")
        report = self.blocker_report()
        if report:
            for i, (cid, entry, deps) in enumerate(report, 1):
                err = entry.get("error") or entry.get("detail") or "no detail recorded"
                lines.append(f"{i}. **{cid}** — {err}")
                if deps:
                    lines.append(
                        f"   - blocks {len(deps)} test(s): {', '.join(deps)}"
                    )
        else:
            lines.append("- None: no failed test is currently blocking other tests.")
        lines.append("")

        phases = [
            ("basic", "Basic EPP operations"),
            ("dnssec", "DNSSEC (secDNS-1.1) operations"),
        ]
        for phase, title in phases:
            lines.append(f"## {title}")
            lines.append("")
            lines.append("| Test | Description | Status | Last error / note | Since |")
            lines.append("|------|-------------|--------|-------------------|-------|")
            rows = [
                (cid, t) for cid, t in sorted(
                    self.state["tests"].items(),
                    key=lambda kv: (0 if kv[1].get("phase") == phase else 1,
                                    kv[0]),
                ) if t.get("phase") == phase
            ]
            if not rows:
                rows = [(cid, t) for cid, t in sorted(self.state["tests"].items())
                        if t.get("phase") == phase]
            for cid, t in rows:
                status = t.get("status")
                symbol = _SYMBOL.get(status, "—") if status else "PENDING"
                err = t.get("error") or ""
                if t.get("denic_codes"):
                    err = f"{err} (DENIC {', '.join(t['denic_codes'])})"
                if status == BLOCKED and t.get("blocked_by") and "blocked by" not in err:
                    err = f"{err} — blocked by {t['blocked_by']}" if err else f"blocked by {t['blocked_by']}"
                lines.append(
                    f"| `{cid}` | {t.get('name', '')} | {symbol} | {err or t.get('detail', '') or '—'} | {t.get('last_run') or 'never'} |"
                )
            lines.append("")

        if self.state["runs"]:
            lines.append("## Run history")
            lines.append("")
            lines.append("| When | Pass | Fail | Blocked | Pending |")
            lines.append("|------|------|------|---------|---------|")
            for r in reversed(self.state["runs"][-20:]):
                lines.append(
                    f"| {r['ts']} | {r['pass']} | {r['fail']} | {r['blocked']} | {r['pending']} |"
                )
            lines.append("")
        lines.append(
            "> Chain under test: EPP client → DAMSR → rEngin → multiplexer → DENIC OTE. "
            "Errors in any link show up here; use the DENIC codes to tell registry "
            "rejections from translation/transport failures."
        )
        lines.append("")
        return "\n".join(lines)
