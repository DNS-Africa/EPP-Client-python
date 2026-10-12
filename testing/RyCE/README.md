# RyCE (.wien / RyCE OTE) EPP Test Suite

End-to-end test suite for the RyCE OTE (.wien) zone that exercises the full
software chain:

```
this suite (EPP client) → DAMSR → rEngin → RyCE OTE (.wien)
```

The suite talks **EPP** to the DAMSR front door in the k8s dev cluster
(namespace `ryce-dev`, host `ryce-epp-dev.dns.net.za:3121`). Everything that
goes wrong in DAMSR, rEngin, or the OTE shows up here as an EPP result code.

The suite is a focused port of `testing/gia` with one critical addition:
**domain:info on a domain with a DNSSEC DS record must return 1000 with a
well-formed response** — regression for **GW-4238** (missing `secDNS`
namespace declaration on the `<epp>` root when a secDNS extension is emitted).

## Running

```shell
python3 -m suite                       # from testing/RyCE/
python3 -m testing.RyCE.suite          # from the repo root (if importable)
```

Useful flags:

| Flag | Effect |
|------|--------|
| `--phase basic\|dnssec\|all` | Run one phase only (default `all`) |
| `--only b-dom-create,s-dom-create,s-secdns-add,b-dom-info-dnssec` | Run only these case ids |
| `--keep` | Skip cleanup cases (leave created domains/contacts on the registry) |
| `--verbose` | Log every request/response pair to the console |
| `--env FILE` | Alternative env file (defaults to `testing/RyCE/.env`) |
| `--out DIR` | Alternative checklist location |

Stdlib only — no pip dependencies.

## Checklist

After **every** case the suite updates a persistent checklist:

- `testing/RyCE/checklists/checklist.json` — machine-readable state
- `testing/RyCE/checklists/CHECKLIST.md` — human-readable, with:
  - the **Currently blocking** section,
  - per-test status (`PASS` / `FAIL` / `BLOCKED` / `PENDING`),
  - the last 20 runs (pass/fail/blocked counts).

A test is **BLOCKED** when one of its prerequisites failed or is itself
blocked; the checklist traces the chain to the root cause.

## Test phases

### Basic (`b-*`)

Session and core EPP operations: connect, login, domain check/create/info/
update/delete, contact lifecycle, poll.

### DNSSEC (`s-*`) + GW-4238 regression

A second session logs in with the `secDNS-1.1` extension on a dedicated
domain:

| Case | What it checks |
|------|----------------|
| `s-connect` / `s-login` | greeting advertises secDNS; login with the extension |
| `s-dom-create` | create the DNSSEC target domain |
| `s-secdns-add` | `domain:update` + `<secDNS:update><secDNS:add>` (RFC 5910) with a generated DS record (RSASHA256/SHA-256) |
| **`b-dom-info-dnssec`** | **`domain:info` on the DS-carrying domain → 1000, well-formed (GW-4238)** |
| `s-secdns-info` | `domain:info` returns the DS in the `<secDNS:infData>` response extension |
| `s-secdns-rem` | `domain:update` + `<secDNS:rem>` (full dsData) removes it |
| `s-secdns-info-after-rem` | no DS data remains |
| `s-secdns-rem-missing` | removing a DS that was never added → `2303`/`2304`/`2306` |
| `s-dom-delete` | cleanup |
| `s-logout` | clean logout |

## Configuration

Credentials and test data live in `testing/RyCE/.env` (do not commit real
values). Real environment variables of the same name override the file, so
CI can inject secrets.

| Key | Purpose |
|-----|---------|
| `EPP_HOST`, `EPP_PORT`, `EPP_TIMEOUT` | EPP edge endpoint |
| `EPP_USER`, `EPP_PASSWORD` | registrar (RAR) login |
| `EPP_CLIENT_CERT`, `EPP_CLIENT_KEY` | optional mutual-TLS client cert/key (PEM) |
| `W_TAKEN_DOMAIN` | known-registered label for the taken-check |
| `W_NS1`…`W_NS4` | nameservers (1/2 initial, 3/4 post-update) |
| `W_CREATE_ROLES` | comma-separated roles required by `.wien` create |
| `W_CONTACT_NAME/CITY/CC/EMAIL` / `W_CONTACT_PHONE` | contact test data |

## Self-healing on re-runs

Create cases retry after deleting a same-named leftover (crashed previous
run). The taken-check and missing-checks use per-run random labels so they
stay deterministic between runs.

## GW-4238

`b-dom-info-dnssec` is the regression test for GW-4238: `domain:info` on a
domain that carries a DS record must return **1000** with a well-formed
response. Before the fix, the OTE/rEngin response builder emitted a `secDNS`
extension without declaring the `secDNS` namespace on the root `<epp>`
element, so DAMSR parsed it as `unknown namespace prefix 'secDNS'` and
surfaced a **2400** to the registrar instead of the real 1000.
