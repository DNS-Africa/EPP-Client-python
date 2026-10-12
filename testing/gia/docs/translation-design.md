# DENIC RRI ↔ EPP Translation Layer — Design

Design and implementation reference for the translation layer that lets rEngin
talk to the DENIC .de registry (RRI protocol v5.0) through the existing
Gateway, so rEngin's core (policy engine, Gateway, poller) keeps consuming
EPP while the wire carries RRI.

> Companion to the protocol reference library in this directory:
> [protocol-overview.md](protocol-overview.md), [error-codes.md](error-codes.md),
> [commands/](commands/README.md), [messages/](messages/README.md).
> The draft [epp-mapping-notes.md](epp-mapping-notes.md) predates this design;
> where the two differ, **this document is authoritative** (notably: success
> maps to EPP `1000`, not `2500` — see [Result mapping](#result-mapping)).

## Table of Contents

- [Layering](#layering)
- [Pluggable Translation Services](#pluggable-translation-services)
- [Request Direction](#request-direction)
- [Response Direction](#response-direction)
- [Context / Operation Semantics](#context--operation-semantics)
- [Result Mapping](#result-mapping)
- [DENIC → EPP Code Mapping](#denic--epp-code-mapping)
- [Status and Field Mapping](#status-and-field-mapping)
- [Poll Contract](#poll-contract)
- [Where Translation Runs](#where-translation-runs)
- [Alternative Considered: XSLT](#alternative-considered-xslt)
- [Known Limitations (v1)](#known-limitations-v1)
- [Implementation Files](#implementation-files)

---

## Layering

```
Policy engine (DomainPolicy, ContactPolicy, …)      ← speaks EPP only
        │  EPP request data (local().request)
        ▼
Gateway (Gateway.py)                                 ← template rendering,
        │  renders the per-transport Jinja2 template      zone resolution,
        ▼                                                   response parsing
Driver (gwlib): gRPCClient → multiplexer, or EPPClient
        │  template output (RRI XML for DENIC)
        ▼
Translation services (elib/translation/)             ← this layer
        │  EPP-in → RRI-out (request)
        │  RRI-in → EPP-out (response)
        ▼
Wire (RRI XML over TCP+TLS via the multiplexer) → DENIC
```

Rationale:

- **The multiplexer stays protocol-agnostic.** It is a byte pipe that knows
  RRI framing/TLS/login (its `RriDriverFactory`, selected by
  `extra_config->'is_rri'`), but it sends the XML it is given **as-is** and
  returns the raw registry response **untranslated**. All semantic
  translation therefore lives in rEngin, next to the EPP knowledge the policy
  engine relies on.
- **The rEngin core stays EPP-only.** `Gateway.processResponse`, the poller
  (`process_poll_messages`), `EppMetadata`, and all `elb`/policy code read EPP
  XPaths. They are never aware that the wire is RRI.
- **Translation is per-transport, not global.** A single rEngin instance may
  serve EPP registries and DENIC at the same time; the translator is chosen
  from each transport's `extra_config`, so nothing in the shared path changes
  for existing EPP transports.

## Pluggable Translation Services

Translation is a pluggable service pair, configured per transport via
`transport.extra_config` (JSONB):

```json
{
    "is_rri": true,
    "grpc_host": "multiplexer",
    "grpc_port": 50051,
    "request_translation":  "elib.translation.denic_rri:translate_request",
    "response_translation": "elib.translation.denic_rri:translate_response"
}
```

| Key | Purpose |
|-----|---------|
| `request_translation` | `module.path:function` for the EPP→wire direction. Absent/empty → identity. |
| `response_translation` | `module.path:function` for the wire→EPP direction. Absent/empty → identity. |
| `is_rri` | Marker the multiplexer uses to select the RRI driver (not read by rEngin). |

The two directions are independent: a transport may enable only one
(for example, responses only, when command requests are authored as RRI
templates — see [Request Direction](#request-direction)).

Service loading lives in `src/lib/elib/translation/__init__.py`:

- A reference is `"module.path:function"`, resolved with
  `importlib.import_module` + `getattr`.
- A missing module, missing function, non-callable, or malformed reference
  raises `TranslationError`.
- Both drivers catch it in `__init__` and raise `ClientException`
  ("translation service misconfigured: …"), so a misconfigured transport fails
  **fast at connection time**, not on the first request.

The translator contract is a single callable:

```python
def translate(xml: str, context: dict | None = None) -> str:
    """Translate one XML document; return the translated XML string.

    context carries driver context (operation name) and may be None.
    """
```

## Request Direction

`elib.translation.denic_rri:translate_request(xml, context=None)` receives the
rendered template output and returns RRI wire form. It dispatches on the root
element:

| Input root | Handling |
|------------|----------|
| `registry-request` (DENIC `global` ns) | Already RRI (template-authored). Ensures a `<ctid>` is present and non-empty (generates one otherwise). Returned unchanged apart from the XML declaration. |
| `epp` containing a recognised primitive command | Translated inline, see below. |
| `epp` containing any other command | `TranslationError` — object commands have no EPP→RRI translation; the transport's template must author the RRI request. |
| anything else | Passed through with a warning (visible, not fatal). |

### Command requests: RRI Jinja2 templates

**Object commands (domain:*, contact:*) are authored directly as RRI in
per-transport Jinja2 templates** — the same template mechanism every other
transport uses (templates are stored in the database per transport/slug).
There is deliberately **no EPP→RRI command mapping** in the translator:

- The DENIC object model is not a superset-compatible rewrite of EPP
  (inline `dnsentry:` instead of host objects, KVK verification, two-step
  AuthInfo flows). A mechanical namespace/element rewrite of an EPP template
  would produce plausible-looking but wrong RRI.
- Authoring the RRI template directly makes the actual wire payload explicit,
  reviewable, and testable against the DENIC examples in
  [commands/](commands/README.md), with no hidden transformation layer.

Template variables are the same flattened EPP request dict every other
transport's template receives (see `Gateway.__getTemplateContent` /
`xml2json.elem2dict`): the top-level key is `command`, namespaced EPP tags
are flattened to their local names, and list-like repetitions become arrays.
For a domain check request the relevant variables are `command.check.name`
and `command.clTRID`.

Example template (domain check, slug `{wid}_Domain_Check`):

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<registry-request xmlns="http://registry.denic.de/global/5.0"
                  xmlns:domain="http://registry.denic.de/domain/5.0">
    <domain:check>
        <domain:handle>{{ command.check.name }}</domain:handle>
    </domain:check>
    <ctid>{{ command.clTRID | default("__CLTRID__") }}</ctid>
</registry-request>
```

Reusing the registrar's `clTRID` as the RRI `ctid` keeps the wire
transaction id correlated with the incoming EPP request (and with
`EppMetadata` audit rows). RRI requires ctids to be 3–64 characters and
unique per session — an EPP clTRID (max 36 chars) fits, but a reused ctid
yields DENIC code `63000060504` (mapped to EPP `2004`).

The `__CLTRID__` placeholder is the safe default: the driver substitutes it
with a generated unique value before translation (the same value is passed
as the gRPC `client_trid`). The `| default("__CLTRID__")` filter falls back
to the placeholder when the registrar sent no `clTRID`. If a template has
neither a ctid value nor the placeholder, the translator generates one
(`DNS-GW-<ts>.<rand>`).

The response the registry returns is translated back to EPP by
`translate_response` before the Gateway parses it, so the policy engine
sees a normal `domain:chkData`.

### Driver-inline EPP primitives

The driver constructs four requests itself (they are not policy-driven, so
there is no template for them). These are the only EPP requests a DENIC
transport ever receives, and the translator maps each one:

| EPP primitive | RRI equivalent | Notes |
|---------------|----------------|-------|
| `poll op="req"` | `<msg:queue-read/>` | |
| `poll op="ack"` (msgID) | `<msg:delete msgid=… msgType=…/>` | The EPP msgID carries `"{msgid}\|{msgType}"` (encoded by the response translator); it is split back here. Without a `\|` the msgType defaults to `domainStatusUpdate`. |
| `hello` | `<msg:queue-read/>` | RRI has no hello; a queue-read peek is a harmless keepalive. |
| `login` (clID/pw) | `<login><user/><password/></login>` | |

## Response Direction

`elib.translation.denic_rri:translate_response(xml, context=None)` converts an
RRI `registry-response` into the EPP `<epp><response>…</response></epp>` form
the rEngin core parses:

- `tr:stid` → `epp:trID/epp:svTRID`
- `tr:ctid` (echoed when sent) → `epp:trID/epp:clTRID` (generated if DENIC
  did not echo one, e.g. because the request had no ctid)
- `tr:result` + `tr:message` list → `epp:result/@code` + `epp:msg`
  (+ `epp:extValue/epp:reason` carrying the original DENIC code)
- `tr:data` children → `epp:resData` children (mapped, see
  [Status and Field Mapping](#status-and-field-mapping))

An input that is already an `epp` root is returned unchanged (idempotency),
and an unrecognised root is passed through with a warning.

## Context / Operation Semantics

The DENIC protocol has no way to distinguish "queue-read of an empty queue"
from any other successful command: both are a bare `success` with no
`tr:data`. The EPP poll contract, however, *requires* `1300` (no messages)
vs `1301` (message available) plus an `epp:resData/epp:msgQ` payload. The
driver therefore passes the operation it just sent in the response
translator's context:

| `context["operation"]` | Set by | Effect on translation |
|------------------------|--------|-----------------------|
| `"poll"` | `driver.poll()` | A `success` result is forced to EPP `1301` (with `msgQ`) when `tr:data` carries `msg:message` entries, else `1300` with an empty `msgQ`. A `failed` queue-read keeps its mapped `2xxx` code **without** a `msgQ`, so the poller stops the cycle instead of retrying a `1xxx`. |
| `"poll_ack"` | `driver.poll_ack()` | No special-casing: a successful `msg:delete` is a plain `1000`. |
| command event name (e.g. `"Create"`, `"Check"`) | `driver.request()` | Plain result mapping; `tr:data` is mapped into `resData`. |

The EPP `msgQ/@id` is encoded as `"{msgid}|{msgType}"` so the poll-ack can be
translated back into `msg:delete msgid=… msgType=…` (EPP's `msgQ` carries a
single `@id` for the queue, while DENIC's delete needs both).

## Result Mapping

rEngin's success convention is `code[0] == '1'` (the 1xxx range); login
success is `1000`; the poller stops on `1300` or any `2xxx`.

| DENIC `tr:result` | Messages | EPP result |
|-------------------|----------|------------|
| `success` | none, or info-level only | `1000`, `msg` = last info text or "Command completed successfully" |
| `success` | warning/error level present | `1000` (still a success — the command took effect), with the warning text in `epp:msg` and `DENIC <code>: <text>` in `extValue/reason` |
| `failed` / `exception` | any | mapped `2xxx` code, `msg` = the worst message text, `extValue/reason` = `DENIC <code>: <text>` |

"worst" picks the most severe `tr:message` (error > warning > info, last
entry wins on ties). Only the **code** is branchable — never the human
readable text (DENIC's own guidance).

## DENIC → EPP Code Mapping

Explicit table (`CODE_MAP` in `denic_rri.py`), covering the codes rEngin's
policies and drivers actually branch on:

| DENIC code | Condition | EPP code |
|------------|-----------|----------|
| `63300062009` | Domain does not exist | `2303` |
| `63310062004` | Domain already exists | `2305` |
| `63370088701` | AuthInfo does not match | `2202` |
| `63650063609` | Message id does not exist | `2303` |
| `63650063607` | Message is not the oldest | `2306` |
| `63100064002` | Authorization failure | `2201` |
| `53000020002` | Unauthorized request | `2201` |
| `83000000010` | Login failed | `2201` |
| `53000020013` | Signature verification failed | `2201` |
| `63100020005` | Login limit / too many failed logins | `2502` |
| `53000000012` | Concurrent write access prohibited | `2400` |
| `76000000001` | Registry service temporarily unavailable | `2400` |
| `53000000008` | Daily quota exceeded | `2400` |
| `53300100021` | Predelegation check problem (retry) | `2400` |
| `83000000004` | XML schema validation failed | `2002` |
| `83000000000` | Request message too long | `2002` |
| `63000060504` | CTID reused | `2004` |

Any DENIC code not in the table maps to `2400` ("try again later") — a
permanent-unknown failure must never look like success, and the original code
is always preserved in `extValue/reason`. The full DENIC table is in
[error-codes.md](error-codes.md); extend `CODE_MAP` as new policies branch on
more codes.

## Status and Field Mapping

| DENIC (response `tr:data`) | EPP (response `resData`) |
|----------------------------|--------------------------|
| `domain:checkData` (`handle`, `status`) | `domain:chkData` (`domain:name`, `domain:avail` — `1` only when status is `free`, `0` for every other status: connect, pendingCreate, serverHold, failed, invalid, redemptionPeriod) |
| `domain:infoData` | `domain:infData`: `handle`→`name`; `status`→`status` (below); `domain:contact role=…`→`domain:contact type=…` (below); `dnsentry:dnsentry xsi:type="dnsentry:NS"` → `ns/hostObj` (unique host names, in order; inline glue and other record types ignored); `regAcc/regAccId`→`clID`; `registrationDate`→`crDate`; `authInfo`→`authInfo attr="pw"` |
| `contact:infoData` | `contact:infData`: `handle`→`id`; other fields namespace-rewritten |
| `msg:message` (non-poll) | payload namespace-rewritten (kept visible) |
| anything else | namespace-rewritten fallback (element names preserved, DENIC namespaces → EPP namespaces) so new payload types are surfaced rather than silently dropped |

Domain status values:

| DENIC `domain:status` | EPP `domain:status/@s` |
|-----------------------|------------------------|
| `connect` | *(healthy — no status element)* |
| `pendingCreate` | `pendingCreate` |
| `serverHold` | `serverHold` |
| `redemptionPeriod` | `redemption` |
| `failed` | `serverHold` |
| `invalid` | `serverHold` |

Contact roles:

| DENIC `domain:contact/@role` | EPP `domain:contact/@type` |
|------------------------------|----------------------------|
| `holder` | `registrant` |
| `admin` | `admin` |
| `tech` | `tech` |
| `billing` | `billing` |
| other | *(dropped in v1)* |

## Poll Contract

`Gateway.process_poll_messages()` expects the standard EPP poll shape; the
translation satisfies it:

1. **Message available** — EPP `1301`, `resData/msgQ/@id = "{msgid}|{msgType}"`,
   one `epp:msg` per `msg:message` with the payload namespace-rewritten.
   For domain payloads the DENIC `handle` is promoted to `domain:name` so
   `PolicyExec.get_object_details()` can resolve the object.
2. **Queue empty** — EPP `1300` with an empty `msgQ` (the poller then stops
   the cycle and waits for the next poll timer).
3. **Failed queue-read** — mapped `2xxx` code, no `msgQ` (poller stops the
   cycle; a `1xxx` here would loop the poller).

## Where Translation Runs

- **`gRPCClient.request()`** (primary DENIC path, via the multiplexer):
  renders the template → substitutes `__CLTRID__` → `_translate_request` →
  gRPC `RegistryCall` → stores the **wire** form in `_sent_data` and the raw
  RRI response in `_response_data` (metadata therefore shows exactly what hit
  the wire) → returns `_translate_response(…, context={"operation": eventName})`.
- **`gRPCClient.poll()` / `poll_ack()`** — build the EPP poll/ack XML, then
  run it through `_send_poll_xml(…, operation="poll" | "poll_ack")` with the
  same translate/store/translate flow.
- **`EPPClient.__request()`** — same hooks (`__CLTRID__` substitution,
  `_translate_request` before `send`, `_translate_response` on the raw read,
  operation context passed by `poll()`/`poll_ack()`). Note the
  [framing caveat](#known-limitations-v1): the built-in driver's socket framing
  is EPP's, so RRI traffic runs through the multiplexer driver.

## Alternative Considered: XSLT

Mapping RRI↔EPP is largely a structural transformation, so an XSLT stylesheet
per direction was the natural alternative (and would also have covered the
EPP→RRI command mapping the template approach avoids). It was rejected:

- The repo is 100% Python with no XSLT processing dependency; adding an
  lxml-xslt (or `xsltlib`) toolchain to the runtime image for one registry is
  a disproportionate supply-chain cost.
- The mappings that matter (result-code folding, poll 1300/1301 forcing,
  status/role tables, msgid round-trip) are *conditional, data-driven*
  decisions — cleaner in 300 lines of reviewed Python with unit tests than in
  XSLT predicates.
- Templates-as-wire-format already puts the RRI payload in front of the
  reviewer; XSLT would hide half of it inside a transform.

Revisit only if a second non-EPP registry joins with a very different object
model and the duplication of hand-written mappers becomes painful.

## Known Limitations (v1)

- **Fields without an EPP home are dropped** from response data: `ace`
  (registry account/quotas), non-NS `dnsentry:` records (A/AAAA glue, MX,
  DNSKEY) and the inline glue addresses on NS records, the `changed` flag, and
  `verification:` (KVK) blocks. The namespace-rewrite fallback keeps unknown
  *elements* visible in `resData`; it is the deliberately-mapped fields above
  that are discarded. `regAcc/regAccId` (→ `clID`) and `dnsentry:NS`
  (→ `ns/hostObj`) *are* mapped — `clID` because EPP mandates it and
  `Gateway.processDomainInfoResponse` reads it, and the NS records because
  without them the local mirror sees a domain with no nameservers and drops any
  host links it has (see the field table above).
- **Poll replay timers reuse the EPP trID, not the DENIC msgid.**
  `create_poll_timer()` keys the replay timer on the response's
  `clTRID`/`svTRID` (translated from DENIC's `ctid`/`stid`). The DENIC queue
  `msgid` is only carried in `msgQ/@id` for the ack, so a replay timer cannot
  be traced back to a specific DENIC queue entry. Object resolution works via
  the promoted `domain:name` (or the contact `id`), so timers are created for
  domain/contact messages whose object exists locally — the same behaviour rEngin
  already has for EPP registries; non-domain/contact payloads or messages
  referencing an unknown object produce no replay timer.
- **One message per EPP poll response.** EPP `msgQ` carries a single `@id`;
  when DENIC returns multiple queued messages the `msgQ/@id` encodes the
  first message's `msgid|msgType` (the extra messages are still emitted as
  `epp:msg` elements).
- **Framing: RRI runs via the multiplexer.** EPPClient's socket framing
  (4-byte prefix over the *total* message) differs from RRI's (4-byte prefix
  over the payload only), plus RRI TLS/session handling, so the DENIC
  transport must use `Source = elib.gwlib.gRPCClient` with the multiplexer's
  RRI driver. The EPPClient translation hooks exist for symmetry, testing,
  and future direct-connect drivers.
- **ctid uniqueness is the caller's responsibility** via `__CLTRID__`
  substitution; a collision produces `63000060504` → EPP `2004` on retry.
- **AuthInfo two-step flows** (`domain:createAuthInfo1/2`,
  `deleteAuthInfo1`) have no EPP equivalent and are not translated; if they
  are needed they must be added as template + translator support.

## Implementation Files

| File | Purpose |
|------|---------|
| `src/lib/elib/translation/__init__.py` | Service loader: `load_request`, `load_response`, `identity`, `TranslationError` |
| `src/lib/elib/translation/denic_rri.py` | DENIC RRI↔EPP translator: `translate_request`, `translate_response`, code/status/role tables |
| `src/lib/elib/gwlib/gRPCClient.py` | Driver hooks (`request`, `_send_poll_xml`, `poll`, `poll_ack`) — the DENIC path |
| `src/lib/elib/gwlib/EPPClient.py` | Driver hooks in `__request`, `poll`, `poll_ack` |
| `tests/unit/test_elib_translation.py` | Unit tests: loader, request/response mapping, poll contract, driver hooks |
| `tests/integration/test_elib_gwlib_grpc_translation.py` | In-process gRPC server test: driver + translation end-to-end over the wire |
| `proto/mp_request.proto` + `proto/mp_request_pb2*.py` | gRPC protocol to the multiplexer (unchanged by this layer) |

Transport configuration (example):

```sql
UPDATE transport
SET source = 'elib.gwlib.gRPCClient',
    url = 'denic-registry.example', port = 7002,
    extra_config = '{
        "is_rri": true,
        "grpc_host": "multiplexer",
        "grpc_port": 50051,
        "request_translation": "elib.translation.denic_rri:translate_request",
        "response_translation": "elib.translation.denic_rri:translate_response"
    }'::jsonb
WHERE name = 'denic-de';
```
