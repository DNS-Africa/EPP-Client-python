# DNSSEC (secDNS-1.1) — current failures

**Status as of 2026-10-12** (gia-dev, RFC 5910 requests that validate against `DAMSr/schemas/secDNS-1.1.xsd`)

## History: the old "connection dropped" diagnosis was a client bug

Earlier runs sent `<add><domain:secDNS:add …>` / `<info><domain:secDNS:info>` /
`<rem><domain:secDNS:rem>`. EPP has no such commands, and `domain:secDNS:add`
is not even a legal QName (two colons), so the request was not
namespace-well-formed XML. The suite now sends RFC 5910 requests:

```xml
<update><domain:update xmlns:domain="urn:ietf:params:xml:ns:domain-1.0">
  <domain:name>giadsNNNNNN.com</domain:name>
</domain:update></update>
<extension><secDNS:update xmlns:secDNS="urn:ietf:params:xml:ns:secDNS-1.1">
  <secDNS:add><secDNS:dsData>…keyTag/alg/digestType/digest…</secDNS:dsData></secDNS:add>
</secDNS:update></extension>
```

DS data is read back from the `domain:info` response `<extension><secDNS:infData>`.

## Results per zone

| Zone | add | info | rem | Root cause (chain side) |
|---|---|---|---|---|
| .com (Verisign OTE) | 1000 | DS present in `secDNS:infData` | **2303** "DNSSEC DS Data does not exist for deletion" | `secDNS:rem` matching fails. It fails with the exact dsData just added (lower- or upper-case digest), and `<secDNS:rem><secDNS:all>true</secDNS:all>` also returns 2303 "Object does not exist". Look at rEngin's DS rem lookup and the translation to the Verisign command. |
| .de (DENIC OTE) | **2002** "Validation of XML request against Schema failed" (DENIC 83000000004) | — | — | DENIC rejects the RRI the translation layer produces for a DS add. The EPP input validates, so the EPP→RRI DS mapping (`dnsentry` DNSKEY) is invalid. |
| .africa (RA OTE) | not reached | | | Blocked by `b-dom-create` / `s-dom-create` (see below) |

## .africa: supporting-contact creation (not DNSSEC, but blocks it)

`domain:create` → `2308 "Unable to create supporting contact … epp-dev.registry.africa:
XML failed EPP schema check: Element 'contact:street': This element is not
expected. Expected is (contact:city)."` The suite's own `contact:create` is
RFC 5733-ordered and accepted by the edge (`b-ct-create` PASS). It is
rEngin's generated contact:create to RA that serializes `addr` out of order.
The suite used to work around this by sending `cc, city, pc, street`, which
broke every contact create once DAMSR started schema-validating (2001).
