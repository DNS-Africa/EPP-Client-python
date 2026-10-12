# DENIC .de Registry — Protocol Reference Library

Reference material extracted from the official DENIC registry documentation
([docs.denic.de](https://docs.denic.de/en/Content/LandingPages/%C3%9Cbersicht.htm),
"Registration System for .de" / RRI, protocol version 5.0) to support building a
translation layer between the DENIC RRI protocol and EPP in rEngin's Gateway.

DENIC does **not** speak EPP. It speaks its own XML protocol over TCP ("RRI" —
Realtime Registry Interface). This library catalogues every XML request/response
example published by DENIC and serves as the fixture reference for the
DENIC↔EPP translation layer implemented in rEngin — see
[translation-design.md](translation-design.md) for the layer's design and
mapping tables.

## Layout

| Path | Contents |
|------|----------|
| [protocol-overview.md](protocol-overview.md) | Transport/framing, message envelope, namespaces, sessions, transaction IDs, K/V vs XML formats |
| [error-codes.md](error-codes.md) | 11-digit message-code structure and the complete DENIC message-code table |
| [translation-design.md](translation-design.md) | **Design & implementation** of the RRI↔EPP translation layer: pluggable services, `extra_config`, mapping tables, poll contract, known limitations |
| [epp-mapping-notes.md](epp-mapping-notes.md) | Draft notes: how DENIC RRI concepts map to EPP (superseded by translation-design.md where they differ) |
| [commands/](commands/README.md) | One file per request command, with the full XML request and response examples (login, logout, regacc:info, domain:*, contact:*, msg:*) |
| [messages/](messages/README.md) | One file per notification-queue (poll) message type, with queue-read/queue-delete XML |
| [schemas/](schemas/README.md) | The XSD schema definitions (global, domain, contact, dnsentry, message, regacc, transaction, verification) |
| [data-model.md](data-model.md) | Field-by-field data-object reference: K/V keyword ↔ XML element, types, value ranges, policies (Domain, Contact, Chprov, RegAcc, data types) |

## Provenance

- Source: https://docs.denic.de — English edition (`/en/`), section "Registration System for .de" (DENIC-29) and the "Examples" section (`Beispiele/50`, protocol 5.0).
- Extraction date: 2026-09-10.
- Each generated file carries a `> Source:` link to the exact documentation page it came from.
- The full offline mirror of the site is stored under `docs/denic/dedocs-Offline/` (HTML; do not commit to git — 91 MB). Re-extract from it if the online docs change.
- DENIC's own guidance: never parse the human-readable error text; branch only on the
  11-digit message code (see [error-codes.md](error-codes.md)).

## Key facts for the translation layer

- Wire format: TCP over TLS; each message is framed with a **4-byte big-endian length prefix** followed by the UTF-8 payload.
- Two payload encodings exist for the same commands: **XML** (primary, schema-validated) and **key/value** text. This library focuses on the XML form.
- Request envelope: `<registry-request xmlns="http://registry.denic.de/global/5.0">` wrapping one command element and an optional `<ctid>` (client transaction id).
- Response envelope: `<registry-response>` → `<tr:transaction>` with `stid` (server tx id), optional `ctid` echo, `result` (`success|failed|exception`), zero or more `<tr:message level= code=>` entries, and an optional `<tr:data>` payload.
- Sessions: `login`/`logout` per connection; RRI Live allows 7 concurrent sessions per RegAcc.
- Notification queue: `msg:queue-read` (poll, by `msgType`) + `msg:delete` (ack by `msgid`), 15 message types — see [messages/](messages/README.md).
