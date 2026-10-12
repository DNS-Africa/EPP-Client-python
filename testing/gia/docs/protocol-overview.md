# DENIC RRI Protocol Overview

The **Realtime Registry Interface (RRI)** is DENIC's wire protocol for the `.de`
registry. It is **not EPP** — it is a custom, length-prefixed XML protocol. This
document summarises the transport and message framing needed to build a
DENIC↔EPP translation layer in rEngin's Gateway.

## Transport

- **Protocol:** TCP over TLS. RRI supports TLS 1.3 (preferred:
  `TLS_AES_128_GCM_SHA256`, Curve 25519) with TLS 1.2 fallbacks.
- **Framing:** each PDU is a 4-byte **big-endian** (network byte order) length
  prefix followed by the UTF-8 payload.
  - Send: write `htonl(len)` then the payload.
  - Receive: read 4 bytes, `ntohl` to get the length, then read that many bytes.
- **Max PDU size:** 64 KB. Exceeding it yields `83000000000`
  ("Request message too long").

> Source: "Reading and Sending Data" (reference implementations in C, PHP,
> Perl, Java) and "Security at the RRI".

## Payload formats (protocol v5.0)

DENIC accepts two equivalent payload encodings for the same commands:

1. **XML** (primary, validated against the published XSDs — see
   [schemas/](schemas/README.md)). Preferred for the translation layer.
2. **Key/Value (K/V)** text format, e.g.:
   ```
   Version: 5.0
   Action: check
   Domain: de-example.de
   ```

Every command page in [commands/](commands/README.md) shows both encodings.

## Request envelope (XML)

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<registry-request xmlns="http://registry.denic.de/global/5.0"
                  xmlns:domain="http://registry.denic.de/domain/5.0">
  <domain:check>
    <domain:handle>de-example.de</domain:handle>
  </domain:check>
  <ctid>optional-client-tx-id</ctid>
</registry-request>
```

- The `<choice>` in `global:requestType` is the authoritative command list:
  `login`, `logout`, `contact:create|update|check|info`,
  `domain:create|update|chholder|delete|restore|check|info|chprov|transit`,
  `domain:createAuthInfo1|createAuthInfo2|deleteAuthInfo1`,
  `regacc:info`, `msg:queue-read`, `msg:delete`.
- `<ctid>` (client transaction id, `tr:idType`, 3–64 chars) is optional;
  reusing a `ctid` returns `63000060504`.

## Response envelope (XML)

```xml
<registry-response xmlns="http://registry.denic.de/global/5.0"
                   xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>server-tx-id</tr:stid>          <!-- 3–64 chars, server-assigned -->
    <tr:ctid>optional-client-tx-id</tr:ctid> <!-- echoed back if sent -->
    <tr:result>success</tr:result>            <!-- success | failed | exception -->
    <tr:message level="info" code="53000080014">
      <tr:text>Domain "Status" is "pendingCreate"</tr:text>
      <tr:argument>optional</tr:argument>
    </tr:message>
    <tr:data>
      <!-- operation-specific data (checkData, infoData, msg:message, ...) -->
    </tr:data>
  </tr:transaction>
</registry-response>
```

- `tr:result` ∈ `success | failed | exception`.
- `tr:message` carries `level` (`info|warning|error`), a 11-digit
  `code` (see [error-codes.md](error-codes.md)), a `text`, and zero or more
  `argument` elements.
- `tr:data` holds the operation-specific payload.

## Sessions

- A connection starts with `<login>` (user + password) and ends with
  `<logout/>`. Authentication is TLS-transport-secured plus the registry's
  own credentials.
- **RRI Live:** up to **7 concurrent sessions** per RegAcc. Throughput is
  200 requests/minute between 02:00–04:00 CE(S)T and 2,000/minute otherwise;
  additional quota is 50,000 requests/day per RegAcc.
- **RRI Rush:** up to 2,000 requests/minute, unlimited RegAccs.
- Reaching the login cap returns `73100000005`; failed logins are rate-limited
  (`63100020005`).

## Notification queue

Asynchronous events are delivered via a per-RegAcc queue (see
[messages/](messages/README.md)):

- Poll: `<msg:queue-read msgType="..."/>` returns the next message in
  `<tr:data>` as a `msg:message`.
- Ack: `<msg:delete msgid="..." msgType="..."/>` removes the oldest message.

## Namespaces

| Prefix | URI |
|--------|-----|
| (default) | `http://registry.denic.de/global/5.0` |
| `domain` | `http://registry.denic.de/domain/5.0` |
| `contact` | `http://registry.denic.de/contact/5.0` |
| `dnsentry` | `http://registry.denic.de/dnsentry/5.0` |
| `verification` | `http://registry.denic.de/verification/5.0` |
| `regacc` | `http://registry.denic.de/regacc/5.0` |
| `msg` | `http://registry.denic.de/msg/5.0` |
| `tr` | `http://registry.denic.de/transaction/5.0` |
