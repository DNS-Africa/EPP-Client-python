# b-poll-empty — RESOLVED (was a client bug)

**Status:** PASS since 2026-10-12.

The earlier write-up blamed the chain for dropping the connection on `poll`.
The suite was sending invalid EPP:

```xml
<poll req="1"><poll:msg xmlns:poll="urn:ietf:params:xml:ns:poll-1.0"/></poll>
```

There is no `poll-1.0` namespace and no `req` attribute. Poll is a core
RFC 5730 command (§2.9.2.3), and it is never advertised in the greeting. The
correct request is:

```xml
<poll op="req"/>
```

With that request the edge returns `1301` with
`<msgQ count="596" id="DAMS-POLL-…">` and a `domain:panData` message.

One chain issue remains: an edge that receives XML failing schema
validation should answer `2001`, not close the socket. Today's DAMSR does
answer `2001` for schema violations (see the `contact:addr` order case), so
the earlier drop may have been specific to the unknown root-level element.
