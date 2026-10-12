# XML Schema Reference (XSD)

The DENIC RRI protocol is formally defined by XSD schemas, one per namespace.
The full XSD text for each is reproduced in the files below (copied from the
"Examples → XML Schema" pages of the DENIC documentation). Use these as the
authoritative element/type definitions when building the DENIC↔EPP translation.

| File | Namespace | Defines |
|------|-----------|---------|
| [global.md](global.md) | `registry.denic.de/global/5.0` | Envelope types (`registry-request`/`registry-response`), `login`, `logout`, `requestType` (the `<choice>` listing every command), `responseType` |
| [domain.md](domain.md) | `registry.denic.de/domain/5.0` | All `domain:*` command/data types (`create`, `update`, `check`, `info`, `delete`, `restore`, `chholder`, `chprov`, `transit`, `createAuthInfo1/2`, `deleteAuthInfo1`), `handleType`, `aceType`, `statusType`, `providerType` |
| [contact.md](contact.md) | `registry.denic.de/contact/5.0` | `contact:create/update/check/info`, `handleType`, contact roles, postal data |
| [dnsentry.md](dnsentry.md) | `registry.denic.de/dnsentry/5.0` | `dnsentry:dnsentry` with subtypes `NS`, `A`, `MX`, `DNSKEY` (nameserver, glue, DNSSEC records) |
| [message.md](message.md) | `registry.denic.de/msg/5.0` | `msg:queue-read`, `msg:delete`, `msg:message` and all 15 notification payload types, `msgTypeType` enum |
| [regacc.md](regacc.md) | `registry.denic.de/regacc/5.0` | `regacc:info` and `regacc:infoData` (registrar account data) |
| [transaction.md](transaction.md) | `registry.denic.de/transaction/5.0` | `tr:transaction`, `tr:message`, `tr:data`, `idType`, `resultType`, `codeType`, `levelType` |
| [verification.md](verification.md) | `registry.denic.de/verification/5.0` | KVK identity-verification record (`verificationInformation`) embedded in contact commands |

## Quick structural facts (from the XSDs)

- `global:requestType` = the ordered set of everything a registrar can send
  (login, logout, the 4 contact commands, the 12 domain commands,
  `regacc:info`, and the 2 queue commands) plus an optional `<ctid>`.
- `tr:transaction` = `stid?`, `ctid?`, `result`, `message*`, `data?`.
- `tr:result` enum = `success | failed | exception`.
- `tr:levelType` enum = `info | warning | error`.
- `tr:message` requires `level` and `code` attributes; body is `text` +
  `argument*`.
- `domain:statusType` enum = `free | connect | failed | invalid |
  redemptionPeriod | pendingCreate | serverHold`.
- `msg:msgTypeType` enum = the 15 notification types (see
  [message.md](message.md)).
- Contact `handleType` and domain `handleType` are `token` with min/max length;
  contact handles start with the administering RegAcc id
  (`DENIC-<regaccid>-<memberid>`).
- `verification:verificationInformation` carries KVK claims
  (`verifiedClaims`, `verificationResult`, `verificationReference`,
  `verificationTimestamp`, `verificationEvidence`, `verificationMethod`,
  `trustFramework`).
