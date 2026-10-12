# b-dom-update-ns — superseded

Folded into [ONBOARDING.md](ONBOARDING.md), items 1 and 2.

The original 2303 "Host does not exist" came from rEngin's local host-table
lookup for `hostObj` (`rEngin/src/lib/epp/Domain.py:590`). The earlier claim that
`domain:create` accepts brand-new `hostObj` names was wrong: `ns1`/`ns2.sedoparking.com`
were already in the table. Now that `ns3`/`ns4` are in the table (created
through a hostAttr create), the update gets further and fails with 2400 on the
unguarded `synchroniseDomainHosts` in Domain-Update (`TemplateNotFound 398_Host_Create`).
