# domainUPDATE

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/domainUPDATE.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/domainUPDATE.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:domain="http://registry.denic.de/domain/5.0" xmlns:dnsentry="http://registry.denic.de/dnsentry/5.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <domain:update>
    <domain:handle>domain-example-nsentry.de</domain:handle>
    <domain:contact role="holder">DENIC-1000022-EXAMPLE-XML-PERSON</domain:contact>
    <domain:contact role="abusecontact">DENIC-1000022-EXAMPLE-XML-GR</domain:contact>
    <domain:contact role="generalrequest">DENIC-1000022-EXAMPLE-XML-ABUSE</domain:contact>
    <dnsentry:dnsentry xsi:type="dnsentry:A">
      <dnsentry:owner>domain-example-nsentry.de</dnsentry:owner>
      <dnsentry:rdata>
        <dnsentry:address>81.91.170.12</dnsentry:address>
      </dnsentry:rdata>
    </dnsentry:dnsentry>
  </domain:update>
  <ctid>xml-74ba5156</ctid>
</registry-request>
```

### XML response

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>a503e644-635c-4253-b598-84d0c2296a97</tr:stid>
    <tr:result>success</tr:result>
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
Action: UPDATE
Domain: domain-example-nsentry.de
Holder: DENIC-1000022-EXAMPLE-PERSON
Generalrequest: DENIC-1000022-EXAMPLE-GR
Abusecontact: DENIC-1000022-EXAMPLE-ABUSE
Nsentry: domain-example-nsentry.de IN A 127.0.0.1
```

### Key/Value format response

```
Result: success
STID: afdd1680-6d5e-4e94-a77a-8ef4a267c6b1
Info: 53000080014 Domain "Status" is "pendingCreate"
```
