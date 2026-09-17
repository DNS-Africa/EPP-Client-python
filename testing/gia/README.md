# .de Zone EPP Test Suite

End-to-end test suite for the `.de` zone that exercises the full software
chain:

```
this suite (EPP client) → DAMSR → rEngin → multiplexer → DENIC OTE
```

The suite talks **EPP** to the DAMSR front door in the k8s dev cluster
(namespace `gia-dev`, host `epp-gia-dev.dns.business:3121`). Everything that
goes wrong in DAMSR, rEngin, the multiplexer, or the RRI↔EPP translation
layer shows up here as an EPP result code — and where the translation layer
surfaces it, the original 11-digit DENIC message code alongside
(`DENIC <code>: <text>` in the response).

## Running

```shell
python3 -m suite --env testing/gia/.env            # from testing/gia/
# or
python3 -m testing.gia.suite                        # from the repo root (if importable)
```

Useful flags:

| Flag | Effect |
|------|--------|
| `--phase basic\|dnssec\|all` | Run one phase only (default `all`) |
| `--only b-dom-create,b-dom-info` | Run only these case ids; others keep their previous checklist status |
| `--keep` | Skip cleanup cases (leave created domains/contacts on the registry) |
| `--verbose` | Log every request/response pair to the console |
| `--env FILE` | Alternative env file (defaults to `testing/gia/.env`) |
| `--out DIR` | Alternative checklist location |

Stdlib only — no pip dependencies.

## Checklist

After **every** case the suite updates a persistent checklist:

- `testing/gia/checklist.json` — machine-readable state
- `testing/gia/CHECKLIST.md` — human-readable, with:
  - the **Currently blocking** section: which failed test is holding back the
    rest of the run, and exactly which tests it blocks,
  - per-test status (`PASS` / `FAIL` / `BLOCKED` / `PENDING`), the last error
    with EPP code and DENIC code where present,
  - the last 20 runs (pass/fail/blocked counts).

A test is **BLOCKED** when one of its prerequisites failed or is itself
blocked; the checklist traces the chain to the root cause. Re-running the
suite updates the entries in place — failed tests flip to PASS once the
blocker is fixed, and blocked tests unlock automatically.

## Test phases

### Basic (`b-*`)

Session and core EPP operations:

| Case | What it checks |
|------|----------------|
| `b-connect` | TLS connect + EPP greeting |
| `b-login` | login with `domain-1.0` + `contact-1.0` services |
| `b-dom-check-free` | `domain:check` a fresh label → `avail=1` |
| `b-dom-check-taken` | `domain:check` `denic.de` → `avail=0` (informational) |
| `b-dom-create` | `domain:create` with full `.de` policy (registrant + admin + tech + billing, 2 NS, authInfo) |
| `b-dom-check-created` | `domain:check` after create → `avail=0` |
| `b-dom-info` | `domain:info` reflects name / NS / authInfo / 4 contact roles |
| `b-dom-create-dup` | duplicate create → EPP `2302`/`2305` (object exists) |
| `b-dom-info-missing` | info on unknown domain → `2303` |
| `b-dom-update-ns` | `domain:update` swapping both nameservers |
| `b-dom-info-after-update` | new NS visible, old NS gone |
| `b-dom-delete` | `domain:delete` |
| `b-dom-check-after-delete` | `domain:check` → `avail=1` (or still `avail=0` while the async grace-period suspension is pending) |
| `b-ct-check-free` / `b-ct-create` / `b-ct-info` / `b-ct-update` / `b-ct-delete` / `b-ct-check-after-delete` | contact lifecycle (PERSON contact) |
| `b-ct-info-missing` | info on unknown handle → `2303` |
| `b-poll-empty` | poll the msg queue (read-only, never acks) |
| `b-logout` | clean logout |

### DNSSEC (`s-*`)

A second session that logs in with the `secDNS-1.1` extension, on a dedicated
domain:

| Case | What it checks |
|------|----------------|
| `s-connect` / `s-login` | greeting advertises secDNS; login with the extension |
| `s-dom-create` | create the DNSSEC target domain |
| `s-secdns-add` | `domain:secDNS:add` a generated DS record (RSASHA256/SHA-256, keyTag per RFC 4034) |
| `s-secdns-info` | `domain:secDNS:info` shows the DS record |
| `s-secdns-rem` | `domain:secDNS:rem` removes it |
| `s-secdns-info-after-rem` | no DS data remains |
| `s-secdns-rem-missing` | removing a non-matching DS → `2304` |
| `s-dom-delete` | cleanup |
| `s-logout` | clean logout |

## OTE / translation-layer behaviors (v1, as observed)

Documented so failures are triaged against the chain (DAMSR → rEngin →
multiplexer → OTE) instead of being re-diagnosed as client bugs. The suite
tolerates or asserts on all of these:

- **Namespaced responses.** OTE prefixes every response tag with `epp:`
  (`<epp:result>`, `<epp:msg>`, …); the parser accepts prefixed or plain tags.
- **`avail` as an element.** `domain:check` / `contact:check` return
  `<domain:avail>1</domain:avail>` as a sibling element instead of the
  standard `domain:name/@avail` attribute; both forms are accepted and the
  deviation is flagged in the note.
- **`domain:info` hostObjs.** No `hostObj` elements while the domain is
  `pendingCreate`; once established they carry a trailing dot
  (`ns1.denic.de.`) — compare normalized, never by raw string.
- **`domain:update` element order.** The schema wants `add` before `rem`
  (`rem` first → `2001` "Expected is (domain:chg)").
- **`contact:voice` pattern.** OTE-specific dotted E.164:
  `(+[0-9]{1,3}\.[0-9]{1,14})?` — default `+27.215550101` (override via
  `DE_CONTACT_PHONE`).
- **`contact:id` maxLength 16.** Denic-style 29-char handles are rejected;
  the suite uses short `gia…` handles.
- **Duplicate create = `2302`** (object exists); the suite accepts
  `2302|2305`.
- **Logout success = `1500** ("Command completed successfully; ending
  session"); the suite accepts `1500|1000`.
- **Async delete = `1001`** (pending grace-period suspension); after delete
  `domain:check` keeps reporting `avail=0` until the grace period lapses.
- **Unsupported services drop the connection.** `poll` and
  `domain:secDNS:*` are not advertised in the greeting and OTE closes the
  TCP connection on the command instead of returning an EPP error — those
  cases fail at the transport level on purpose.
- **New nameservers cannot be added.** `host:create` → `2101` (Host Creation
  Unsupported) and OTE validates `hostObj` against its internal host mirror,
  so `domain:update` with a new NS fails `2303` "Host does not exist". The
  NS swap in `b-dom-update-ns` is expected to fail until the chain supports
  host objects (see `docs/translation-design.md`, Known Limitations).

## Configuration

Credentials and test data live in `testing/gia/.env` (do not commit real
values). Real environment variables of the same name override the file, so CI
can inject secrets.

| Key | Purpose |
|-----|---------|
| `EPP_HOST`, `EPP_PORT`, `EPP_TIMEOUT` | EPP edge endpoint |
| `EPP_USER`, `EPP_PASSWORD` | registrar (RegAcc) login |
| `DE_REGISTRANT`, `DE_ADMIN`, `DE_TECH`, `DE_BILLING` | local contact ids with `zone_contact` mappings to DENIC handles |
| `DE_NS1`…`DE_NS4` | nameservers (1/2 initial, 3/4 post-update) |
| `DE_CONTACT_PREFIX` | DENIC RegAcc handle prefix for created contacts |
| `DE_TAKEN_DOMAIN` | domain expected to be registered for the taken-check |
| `DE_CONTACT_NAME/CITY/CC/EMAIL` | contact test data |

## Self-healing on re-runs

Create cases retry after deleting a same-named leftover (crashed previous
run); contact create does the same. The taken-check and missing-checks use
per-run random labels so they stay deterministic between runs.

## Debugging beyond the checklist

- DENIC reference for every RRI command, error code, and schema:
  [`docs/`](docs/README.md).
- When a case fails, read the checklist row for the EPP code; if the DENIC
  code is present, look it up in
  [`docs/error-codes.md`](docs/error-codes.md).
- Translation-layer contract (code/status mapping, poll behaviour, known
  v1 limitations): [`docs/translation-design.md`](docs/translation-design.md).
- To see what actually reached the wire, run with `--verbose` and compare the
  request XML against the RRI examples in `docs/commands/`.
