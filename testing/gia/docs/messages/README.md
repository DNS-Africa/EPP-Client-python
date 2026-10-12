# Notification Queue Message Types

DENIC pushes asynchronous notifications into a per-RegAcc queue. Registrars
poll them with two commands (both shown in every file in this directory):

| Command | Element | Purpose |
|---------|---------|---------|
| queue-read | `<msg:queue-read msgType="..."/>` | Returns the next queued message of the given type (empty `<tr:transaction>` when the queue is empty) |
| queue-delete | `<msg:delete msgid="..." msgType="..."/>` | Removes a specific message from the queue (acknowledgement). Only the **oldest** message of the queue can be deleted — otherwise error `63650063607`. |

Messages carry a `msgid` (3–64 chars, echo it in `queue-delete`), a `msgcnt`
(count of messages in the queue for that type) and a `msgtime` (ISO 8601
enqueued time).

The allowed `msgType` values are enumerated in
[schemas/message.md](../schemas/message.md).

## Message types

| Type | File | Meaning |
|------|------|---------|
| `domainUpdate` | [domainupdate.md](domainupdate.md) | Domain data changed by someone other than this RegAcc |
| `domainStatusUpdate` | [domainstatusupdate.md](domainstatusupdate.md) | Domain status changed (e.g. `connect`, `serverHold`), includes holders and verification deadlines |
| `domainDelete` | [domaindelete.md](domaindelete.md) | Domain was deleted (with reference or reason) |
| `domainTransit` | [domaintransit.md](domaintransit.md) | Domain is in transit |
| `contactUpdate` | [contactupdate.md](contactupdate.md) | Contact data changed |
| `contactDelete` | [contactdelete.md](contactdelete.md) | Contact(s) deleted (one or more handles) |
| `contactVerificationRequired` | [contactverificationrequired.md](contactverificationrequired.md) | Holder verification must be provided to avoid dedelegation/deletion (KVK) |
| `authInfoExpire` | [authinfoexpire.md](authinfoexpire.md) | AuthInfo1 is about to expire (includes expiry date) |
| `authInfo2Notify` | [authinfo2notify.md](authinfo2notify.md) | AuthInfo2 letter was sent to the holder |
| `authInfo2Delete` | [authinfo2delete.md](authinfo2delete.md) | AuthInfo2 deleted / letter could not be delivered |
| `chprovAuthInfo` | [chprovauthinfo.md](chprovauthinfo.md) | AuthInfo set for a provider change (new + old provider) |
| `expireWarning` | [expirewarning.md](expirewarning.md) | Domain renewal deadline approaching |
| `expire` | [expire.md](expire.md) | Domain has expired (includes expiry date) |
| `lockCreate` | [lockcreate.md](lockcreate.md) | Domain was locked by DENIC |
| `lockDelete` | [lockdelete.md](lockdelete.md) | Domain lock was removed |

## Example flow

For `domainStatusUpdate` (full versions in [domainstatusupdate.md](domainstatusupdate.md)):

1. Poll: `<msg:queue-read msgType="domainStatusUpdate"/>`
2. Response contains `<msg:message msgid="..." msgcnt="..." msgtime="...">` with the notification payload inside `<tr:data>`.
3. Ack: `<msg:delete msgid="..." msgType="domainStatusUpdate"/>`
