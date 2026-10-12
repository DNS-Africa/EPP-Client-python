# domainCREATE

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/domainCREATE.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/domainCREATE.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:domain="http://registry.denic.de/domain/5.0" xmlns:dnsentry="http://registry.denic.de/dnsentry/5.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <domain:create>
    <domain:handle>domain-example-nserver.de</domain:handle>
    <domain:contact role="holder">DENIC-1000022-EXAMPLE-XML-PERSON</domain:contact>
    <domain:contact role="abusecontact">DENIC-1000022-EXAMPLE-XML-GR</domain:contact>
    <domain:contact role="generalrequest">DENIC-1000022-EXAMPLE-XML-ABUSE</domain:contact>
    <dnsentry:dnsentry xsi:type="dnsentry:NS">
      <dnsentry:owner>domain-example-nserver.de</dnsentry:owner>
      <dnsentry:rdata>
        <dnsentry:nameserver>ns1.denic.de</dnsentry:nameserver>
      </dnsentry:rdata>
    </dnsentry:dnsentry>
    <dnsentry:dnsentry xsi:type="dnsentry:NS">
      <dnsentry:owner>domain-example-nserver.de</dnsentry:owner>
      <dnsentry:rdata>
        <dnsentry:nameserver>ns1.domain-example-nserver.de</dnsentry:nameserver>
        <dnsentry:address>81.91.170.12</dnsentry:address>
      </dnsentry:rdata>
    </dnsentry:dnsentry>
  </domain:create>
  <ctid>xml-74ba5155</ctid>
</registry-request>
```

### XML response

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>a503e644-635c-4253-b598-84d0c2296a97</tr:stid>
    <tr:ctid>xml-74ba5155</tr:ctid>
    <tr:result>success</tr:result>
    <tr:message level="info" code="53000080014">
      <tr:text>Domain "Status" is "pendingCreate"</tr:text>
    </tr:message>
  </tr:transaction>
</registry-response>
```

### Key/Value format request (alternative wire format)

```
Version: 5.0
Action: CREATE
Domain: domain-example-nserver.de
Holder: DENIC-1000022-EXAMPLE-PERSON
Generalrequest: DENIC-1000022-EXAMPLE-GR
Abusecontact: DENIC-1000022-EXAMPLE-ABUSE
Nserver: ns1.denic.de
Nserver: ns2.denic.de
CTID: cba-987654321
```

### Key/Value format response

```
Result: success
STID: 74ba5119-74d1-4ba6-935f-4feb07ddd14d

INFO: 53000080014 Domain "Status" is "pendingCreate"
STID: 3727d839-497f-4ef9-8aa5-0a1ea16a8c95
CTID: cba-987654321
```
