# Failure diagnostics

One file per failing area of the `.de`/`.com`/`.africa` EPP suite. Each has
the wire-level evidence and which link of `DAMSR → rEngin → multiplexer → OTE`
is at fault.

| Test | Symptom | File |
|---|---|---|
| **.de onboarding** | **Ordered fix list for every failing .de case** | [de/ONBOARDING.md](de/ONBOARDING.md) |
| **.de bug list (13 Oct)** | **Interactive page: POL-1096 + run sheet + suite, split by rEngin / DAMSr / Policy / Templates** | [de/onboarding-bugs.html](de/onboarding-bugs.html) (open locally; GitHub shows HTML as source) |
| `b-dom-update-ns` | .de: 2400, unguarded host sync in Domain-Update (see ONBOARDING). .com: `2001 "Command syntax error"` to an XSD-valid update | [b-dom-update-ns.md](de/b-dom-update-ns.md) |
| `s-secdns-add` / `s-secdns-rem` | .de: Domain_Update context only carries the change (ONBOARDING item 1). .com: add works, rem returns 2303 | [s-secdns-add.md](de/s-secdns-add.md) |
| `b-dom-create` (.africa) | rEngin's supporting contact:create to RA has `addr` children out of RFC 5733 order | [s-secdns-add.md](de/s-secdns-add.md#africa-supporting-contact-creation-not-dnssec-but-blocks-it) |
| `b-poll-empty` | **resolved**: it was a client bug (invalid poll XML) | [b-poll-empty.md](de/b-poll-empty.md) |

Every request the suite sends validates against the RFC XSDs in
`DAMSr/schemas/` (epp, domain, contact, secDNS). A failure here is a chain
response, not malformed client XML.
