# .de onboarding — what still needs fixing

**Run:** 2026-10-12 against gia-dev (`epp-gia-dev.dns.business`, DENIC OTE).
`python3 -m suite --zone de` → 28 PASS, 10 FAIL, 11 BLOCKED (of 49).
Every request the suite sends validates against the RFC XSDs in `DAMSr/schemas/`.
Root causes come from the rEngin traces (`kubectl logs -n gia-dev deploy/rengin`),
the deployed policy (`policy` row `denic`: `GW_DENIC_RELEASE_001, policy_gw_libs_030-5.13.6209-dev`)
and the transport templates (`template` rows for transport 54 `Denic-test`).

**What works today:** domain check, create, info, delete, duplicate/missing errors,
the contact lifecycle, poll, and transfer query / own-domain refusal (answered
locally, see gap 4).

## Fix list (ordered by impact)

### 1. `Domain_Update` gets only the change, but DENIC needs the full domain — rEngin Gateway / template
Fails: `o-dom-update-contact`, `o-dom-update-authinfo`, `s-secdns-add` (and every
other domain update) → `2002 "Validation of XML request against Schema failed"
(DENIC 83000000004)`.

The `Domain_Update` template says it itself: *"DENIC domain:update REPLACES the
complete domain configuration … you must supply the full desired final state"*.
It renders `registrant`, `contact` and `ns`. The gateway passes only the EPP change:

```
{'name': 'giasuite802757.de', 'chg': {'authInfo': {'pw': …}}}
{'name': 'giasuite802757.de', 'add': {'contact': {tech C0003243}}, 'rem': {…}}
{'name': 'giads802848.de', 'ext': {secDNS-1.1: {'add': {'keyData': …}}}}
```

So `<domain:contact role="holder"></domain:contact>` goes out empty with no NS
entries. **Fix:** for the DENIC transport, merge the change onto the domain's
current state (local mirror, or a fresh `Domain_Info`) before rendering
`Domain_Update`, so the context carries the final registrant, contacts, NS
and DNSKEYs.

### 2. NS changes crash on host sync — policy (`policy_gw_libs` Domain-Update)
Fails: `b-dom-update-ns`, `o-dom-update-ns-attr` → `2400 Internal server error`.

`Domain-Update` (deployed policy line ~2396) calls
`Gateway.synchroniseDomainHosts(...)` whenever the payload adds or removes NS.
DENIC has no host templates → `TemplateNotFound: 398_Host_Create` → 2400.
`Domain-Create` already skips this when `SyncDomainHosts` is false; Domain-Update
doesn't check the flag. **Fix:** guard the Domain-Update host sync the same way.
Fix 1 is also needed for the update to be valid at DENIC afterwards.

Related: with `hostObj`, rEngin first requires each host to be in the
registrar's local host table (`rEngin/src/lib/epp/Domain.py:590`, else 2303).
`host:create`/`host:check` are policy stubs (2101) and `host-1.0` isn't
advertised. So for .de the registrar path is `hostAttr`, which already
auto-creates local hosts on create.

### 3. Holder change uses the wrong path — policy + `Contact_Create` template
Fails: `o-dom-chholder` → `2308 "Unable to create supporting contact for
C0003243: … Validation of XML request against Schema failed"`.

- The policy tries to create the new holder at DENIC (`CreateOutstandingContacts`),
  and DENIC rejects the rendered `Contact_Create` RRI for this contact (it has
  `org`, two street lines, `sp`, cc `AI`). Find which field breaks the template.
- After that, the change would go through `Domain_Update`. The transport has a
  `Domain_Chholder` template that nothing calls. DENIC requires `domain:chholder`
  for holder changes (the `Domain_Update` template comment says so too).
  **Fix:** route `domain:update chg/registrant` to `Domain_Chholder`.

### 4. Templates the policy calls but the transport doesn't have — policy vs templates
The deployed .de policy is still the unchanged `.org` copy (`GW_DENIC_RELEASE_001`).

| Policy calls | Transport 54 has | Result |
|---|---|---|
| `Domain_Renew` | — | `o-dom-renew` → **2400** (`TemplateNotFound 398_Domain_Renew`). .de renews automatically, so the policy should answer renew itself: 1000 with the new exDate, or a clean 2101. |
| `Domain_Restore_Request` / `Restore_Report` | `Domain_Restore` | Not reached yet (see 5). |
| `Domain_Transfer_Request/Query/Approve/Reject/Cancel` | `Domain_Chprov` | Inbound transfer (chprov) is unwired. Untested: needs a domain sponsored by a second registrar account. |
| `Host_Create` (host sync) | — | See 2. |
| — | `Domain_Chholder`, `Domain_Create_AuthInfo1/2`, `Domain_Delete_AuthInfo1`, `Domain_Transit` | Never called. AuthInfo changes (`o-dom-update-authinfo`) should use `Domain_Create_AuthInfo1`, not `Domain_Update`. |

### 5. Restore is not available to registrars — DAMSr greeting/schemas + policy
Fails: `o-rfc-greeting-rgp`, `o-dom-restore` → `2001 "… rgp-1.0 update: No
matching global element declaration"`.

`rgp-1.0` isn't advertised, and the DAMSr edge doesn't load `rgp-1.0.xsd` for
validation, so an RFC 3915 restore never reaches rEngin. **Fix:** advertise and
load rgp-1.0, then map the policy's `Restore_Request` to the `Domain_Restore` template.

### 6. Response shape — rEngin / DENIC response translation
Fails: `o-rfc-check-avail`. `domain:check` returns `<domain:avail>1</domain:avail>`
as an element, where RFC 5731 §3.1.1 requires `<domain:name avail="1">`. Strict
EPP clients will not see availability. The `.com` and `.africa` responses are correct.

Also seen (not yet a failing case): the DENIC remote info (`denic.de`) is
emitted with `<domain:contact type="registrant">`, which isn't a valid RFC 5731
contact type. Locally created domains are emitted correctly (`o-rfc-info-fields` PASS).

## Not covered by the suite yet
- Inbound transfer (chprov) from another registrar: needs a second OTE RegAcc.
- `domain:transit` (DENIC-specific, no EPP equivalent).
- Poll message mapping for the 15 DENIC message types: the suite only reads the queue head.

## Re-run
```shell
cd testing/gia && python3 -m suite --zone de
```
The checklist at `checklists/de/CHECKLIST.md` updates in place. Blocked cases
unblock automatically once their root cause is fixed.
