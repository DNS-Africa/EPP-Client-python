# DENIC RRI ↔ EPP Mapping Notes (Draft)

Starting notes for building a translation layer so rEngin can treat DENIC as a
"normal" EPP registry. DENIC's RRI differs from EPP in framing, envelope,
object model and lifecycle semantics. This is an initial catalogue of the
mapping; it will grow as the driver is implemented.

> Status: draft / information-gathering. The translation layer is now
> implemented — see [translation-design.md](translation-design.md) for the
> authoritative design and mapping tables. Where the two documents disagree,
> the design document wins (notably: DENIC `success` maps to EPP `1000`, not
> `2500`; rEngin treats `code[0] == '1'` as success).

## Envelope mapping

| DENIC RRI | EPP |
|-----------|-----|
| `<registry-request>` root | `<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">` |
| command element (e.g. `<domain:check>`) | `<cmd><check><domain:check>…` — one `<cmd>` child per EPP command verb |
| `<ctid>` | `<epp><trID><clTRID>` |
| `<registry-response>` → `<tr:transaction><tr:stid>` | `<epp><trID><svTRID>` |
| `tr:transaction` echo of `<tr:ctid>` | `<trID><clTRID>` |
| `<tr:result>success</tr:result>` | `<epp code="2500">` (or the per-command 2500-range success code) |
| `<tr:result>failed|exception</tr:result>` | `<epp code="4xxx">` (mapped from the DENIC 11-digit code, see below) |
| `<tr:message level= code=>` + `<tr:text>` + `<tr:argument>` | `<epp><msg>` / (optionally) `<value>` |
| `<tr:data>` payload | command-specific response element (`<domain:chkData>`, `<domain:infData>`, …) |

Key consequence: a single DENIC request maps to **one** EPP `<cmd>`, and a DENIC
response's `tr:message` list must be flattened into EPP's single `code`/`msg`
model. DENIC's 11-digit codes are richer than EPP's 4-digit codes, so the
translation must both **collapse** DENIC code → EPP code and **preserve** the
original code (e.g. in a `value` element or a trace field) to avoid losing
diagnostic detail.

## Command mapping

| DENIC RRI | EPP | Notes |
|-----------|-----|-------|
| `login` / `logout` | `login` / `logout` | DENIC uses `<user>`/`<password>`; EPP uses `<clID>`/`<pw>`. AuthInfo/2FA differ. |
| `regacc:info` | no direct EPP equivalent | Nearest: `registrar:info`/`info`. May be a no-op or local lookup. |
| `domain:check` | `domain:check` | Status mapping below. |
| `domain:create` | `domain:create` | Nameservers are **inline** in DENIC (`dnsentry:`) but separate `host:` objects in EPP — see below. |
| `domain:createAuthInfo1` / `createAuthInfo2` | no direct EPP equivalent | Two-step registration with a secret AuthInfo; approximate with `domain:transfer` (info) or keep as a registry-specific extension. |
| `domain:deleteAuthInfo1` | no direct EPP equivalent | Secret-based delete; map to `domain:delete` where possible. |
| `domain:update` | `domain:update` | Contact/DNS changes inline. |
| `domain:info` | `domain:info` | `recursive` attribute has no EPP meaning; `authInfo` is DENIC-specific. |
| `domain:chholder` | `domain:update` (chg holder) | EPP has no dedicated chholder; express as update. |
| `domain:chprov` | `domain:transfer` (request) | Provider change ≈ registrar transfer. |
| `domain:delete` | `domain:delete` | |
| `domain:restore` | `domain:restore` | |
| `domain:transit` | no direct EPP equivalent | Registry-side disconnect/reconnect of DNS service. |
| `contact:create` / `update` / `check` / `info` | `contact:create` / `update` / `check` / `info` | Contact model differs (DENIC flat fields + KVK verification vs EPP vCard). |
| `msg:queue-read` | `poll req` | Poll the queue. |
| `msg:delete` | `poll ack` | Acknowledge a message. |

## Object-model differences

### Nameservers (biggest difference)

- **DENIC:** nameservers and glue are embedded in every domain command as
  `<dnsentry:dnsentry xsi:type="dnsentry:NS|A|MX|DNSKEY">` elements — there are
  **no host objects**.
- **EPP:** nameservers are separate `host` objects (`host:create`,
  `host:info`, `host:add`, `host:chg`) and glue via `host:addr`.

The translation layer must **expand** a DENIC domain command's `dnsentry:`
elements into EPP `host:*` calls on create/update, and **collapse** EPP host
objects back into DENIC `dnsentry:` elements. This is the main place where one
EPP operation fans out into multiple DENIC operations.

### Contacts

- DENIC contact = flat fields (name, organisation, postal, email, phone) plus
  KVK `verification:verificationInformation`.
- EPP contact = vCard (RFC 5589) with `contact:vCard`.
- Mapping: DENIC `type` (PERSON/ORG/REQUEST) → vCard `fn`/`org`/`kinds`; DENIC
  handle (`DENIC-<regacc>-<member>`) ↔ EPP `<contact:id>`.
- KVK verification has no EPP equivalent; carry it in an EPP extension element
  or drop it (decision needed).

### Status mapping

| DENIC `domain:status` | EPP interpretation |
|-----------------------|--------------------|
| `free` | available (`domain:check` → "available") |
| `connect` | active / in use |
| `pendingCreate` | `pendingCreate` status (RFC 5731) |
| `serverHold` | `serverHold` status |
| `failed` | `serverHold` + warning (DENIC predelegation check failed) |
| `invalid` | invalid name (treat as available/`inuse` per DENIC intent) |
| `redemptionPeriod` | `redemption` status (RFC 5731) |

### DNSSEC

- DENIC carries DNSKEY **inline** in domain commands (`dnsentry:DNSKEY`).
- EPP uses the `dnssec` extension (`dnssec:setDS`, `dnssec:remDS`).
- Map inline DNSKEY ↔ `dnssec:setDS` records.

## Poll / notification mapping

- DENIC `msg:queue-read` (per `msgType`) → EPP `poll req` for the object type.
- DENIC `msg:delete` (by `msgid`) → EPP `poll ack`.
- 15 DENIC message types (see [messages/](messages/README.md)) must be mapped to
  EPP `<poll><msg>` payloads. Some have no EPP analogue (e.g. `authInfoExpire`,
  `expire`, `lockCreate`) and may need an extension or be surfaced as registry
  poll messages verbatim.

## Error-code mapping (DENIC 11-digit → EPP 4-digit)

DENIC codes are 11 digits; EPP codes are 4 digits. A translation table must map
each DENIC code to an EPP code. Suggested anchors:

| DENIC condition | Suggested EPP code |
|-----------------|--------------------|
| success | `2500` (generic) / command-specific `2500`-range |
| object does not exist (`63300062009`) | `2303` (object does not exist) |
| object already exists (`63310062004`) | `2101`/`2102` |
| object exists inuse (`domain:check` "connect") | `2304` (object exists) |
| authorization failure (`63100064002`, `53000020002`) | `4201`/`4220` |
| authInfo mismatch (`63370088701`) | `2304`/`2201` |
| concurrent write access (`53000000012`) | `2400` (try again) |
| nameserver/glue errors (`53300102902/12`) | `2004`/`2506` (bad param / status) |
| schema/encoding failure (`83000000004`) | `2002`/`2004` |
| transient registry unavailable (`76000000001`) | `4001` |

> The full DENIC code table is in [error-codes.md](error-codes.md). Because
> DENIC codes encode more than EPP can, the translation should retain the
> original DENIC code alongside the mapped EPP code.

## Open questions (to resolve during implementation)

1. How to represent DENIC's two-step AuthInfo create/delete flows in EPP.
2. Where to carry KVK verification data in EPP (extension vs drop).
3. Exact EPP codes for DENIC-specific poll messages with no EPP counterpart.
4. Contact handle ↔ EPP contact id naming convention.
5. Whether `domain:transit` / `regacc:info` map to anything or are local no-ops.
