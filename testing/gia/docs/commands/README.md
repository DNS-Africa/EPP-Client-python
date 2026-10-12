# Request Commands

Every command is a single element inside the `<registry-request>` envelope
(see [../protocol-overview.md](../protocol-overview.md)). Each file below
contains the official DENIC XML request/response examples plus, where DENIC
documents them, the equivalent key/value (K/V) wire format.

## Session

| Command | Element | Description |
|---------|---------|-------------|
| [login](login.md) | `<login>` | Authenticate the session (user + password) |
| [logout](logout.md) | `<logout/>` | End the session |

## Registrar account

| Command | Element | Description |
|---------|---------|-------------|
| [regacc:info](regaccinfo.md) | `<regacc:info>` | Look up registrar account (RegAcc) details |

## Domain commands

| Command | Element | Description |
|---------|---------|-------------|
| [domain:check](domaincheck.md) | `<domain:check>` | Check domain availability/status (optionally recursive) |
| [domain:create](domaincreate.md) | `<domain:create>` | Register a domain with holder, contacts and name servers |
| [domain:createAuthInfo1](domaincreate-authinfo1.md) | `<domain:createAuthInfo1>` | Two-step registration, step 1 — send SHA-1 hash + expiry of a secret AuthInfo |
| [domain:createAuthInfo2](domaincreate-authinfo2.md) | `<domain:createAuthInfo2>` | Two-step registration, step 2 — finalize after DENIC confirms the AuthInfo |
| [domain:update](domainupdate.md) | `<domain:update>` | Update contacts / DNS entries of an existing domain |
| [domain:info](domaininfo.md) | `<domain:info>` | Read the full domain record (optionally recursive / with authInfo) |
| [domain:chholder](domainchholder.md) | `<domain:chholder>` | Change the domain holder contact(s) |
| [domain:chprov](domainchprov.md) | `<domain:chprov>` | Change the administering provider (requires AuthInfo) |
| [domain:delete](domaindelete.md) | `<domain:delete>` | Delete a domain |
| [domain:deleteAuthInfo1](domaindelete-authinfo1.md) | `<domain:deleteAuthInfo1>` | Delete a domain via the AuthInfo1 (secret) flow |
| [domain:restore](domainrestore.md) | `<domain:restore>` | Restore a domain in `redemptionPeriod` status |
| [domain:transit](domaintransit.md) | `<domain:transit>` | Transfer a domain into/out of registry DNS service (`disconnect` attribute) |

## Contact commands

| Command | Element | Description |
|---------|---------|-------------|
| [contact:create](contactcreate.md) | `<contact:create>` | Create a contact (PERSON/ORG, with verification information; or REQUEST with URI-template) |
| [contact:update](contactupdate.md) | `<contact:update>` | Update a contact |
| [contact:check](contactcheck.md) | `<contact:check>` | Check whether a contact handle exists |
| [contact:info](contactinfo.md) | `<contact:info>` | Read a contact record |

## Notification queue commands

`msg:queue-read` and `msg:delete` have no dedicated example page; every file in
[../messages/](../README.md) shows both requests (a `queue-read` for that
message type, and the `delete` acknowledgement) together with the queued
message. Queue semantics are summarised in [../messages/README.md](../messages/README.md).

## Conventions visible in the examples

- `<ctid>` (client transaction id, 3–64 chars) is optional in requests and
  echoed back in the response; reusing a `ctid` yields error `63000060504`.
- Responses carry a `tr:stid` (server transaction id) and a `tr:result` of
  `success`, `failed` or `exception` plus optional `tr:message` entries whose
  `code` is the 11-digit message code — see [../error-codes.md](../error-codes.md).
- Domain handles are the domain name itself; contact handles look like
  `DENIC-<regaccid>-<memberid>` (e.g. `DENIC-1000022-EXAMPLE-PERSON`).
