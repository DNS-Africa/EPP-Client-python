# domainCHHOLDER

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/domainCHHOLDER.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/domainCHHOLDER.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:domain="http://registry.denic.de/domain/5.0" xmlns:dnsentry="http://registry.denic.de/dnsentry/5.0">
  <domain:chholder>
    <domain:handle>de-example.de</domain:handle>
    <domain:contact role="holder">DENIC-1000002-MAX</domain:contact>
    <domain:contact role="abusecontact">DENIC-1000002-ABUSE</domain:contact>
    <domain:contact role="generalrequest">DENIC-1000002-GENERAL</domain:contact>
    <dnsentry:dnsentry xsi:type="dnsentry:NS">
      <dnsentry:owner>de-example.de</dnsentry:owner>
      <dnsentry:rdata>
        <dnsentry:nameserver>ns1.xn--de-xample-x2a.de</dnsentry:nameserver>
      </dnsentry:rdata>
    </dnsentry:dnsentry>
    <dnsentry:dnsentry xsi:type="dnsentry:NS">
      <dnsentry:owner>de-example.de</dnsentry:owner>
      <dnsentry:rdata>
        <dnsentry:nameserver>ns2.de-example.de</dnsentry:nameserver>
        <dnsentry:address>81.91.170.12</dnsentry:address>
      </dnsentry:rdata>
    </dnsentry:dnsentry>
    <dnsentry:dnsentry xsi:type="dnsentry:NS">
      <dnsentry:owner>de-example.de</dnsentry:owner>
      <dnsentry:rdata>
        <dnsentry:nameserver>ns2.de-example.de</dnsentry:nameserver>
        <dnsentry:addressV6>2001:608:6:6:0:0:0:11</dnsentry:addressV6>
      </dnsentry:rdata>
    </dnsentry:dnsentry>
    <dnsentry:dnsentry xsi:type="dnsentry:DNSKEY">
      <dnsentry:owner>de-example.de.</dnsentry:owner>
        <dnsentry:rdata>
          <dnsentry:flags>257</dnsentry:flags>
          <dnsentry:protocol>3</dnsentry:protocol>
          <dnsentry:algorithm>8</dnsentry:algorithm>
          <dnsentry:publicKey>AwEAAajpN1rjU365IDVSd+duoMg4UF4S8zBSpJ4D/p2VSOKYVN7/0CkAV6pOhmdcoUMETA2LDPBWjEh4rrGiBN9ReRw/4udMgiEf3YyvsJEDpF6vtrWzqe+Cu9iu8QV//8ESlQgqK8TqVcR7e/FPd89R44S68GhZRFGw7h7sDrRnGIZf</dnsentry:publicKey>
        </dnsentry:rdata>
    </dnsentry:dnsentry>
  </domain:chholder>
  <ctid>cba-987654321</ctid>
</registry-request>
```

### XML response

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>538f1687-963a-11df-a9e2-9519b5688882</tr:stid>
    <tr:ctid>cba-987654321</tr:ctid>
    <tr:result>success</tr:result>
    <tr:message level="info" code="53000080013">
      <tr:text>Domain "Status" is "connect"</tr:text>
    </tr:message>
    <tr:message level="info" code="16350000041">
      <tr:text>Verification information must be provided for the holder(s) to avoid deletion by</tr:text>
      <tr:argument>2024-12-16T15:45:01+01:00</tr:argument>
    </tr:message>
    <tr:message level="info" code="16350000040">
      <tr:text>Verification information must be provided for the holder(s) to avoid dedelegation by</tr:text>
      <tr:argument>2024-12-09T15:45:01+01:00</tr:argument>
    </tr:message>
  </tr:transaction>
</registry-response
```

### XML response 2

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>538f1687-963a-11df-a9e2-9519b5688882</tr:stid>
    <tr:ctid>cba-987654321</tr:ctid>
    <tr:result>success</tr:result>
    <tr:message level="info" code="53000080013">
      <tr:text>Domain "Status" is "serverHold"</tr:text>
    </tr:message>
    <tr:message level="info" code="16350000041">
      <tr:text>Verification information must be provided for the holder(s) to avoid deletion by</tr:text>
      <tr:argument>2024-12-16T15:45:01+01:00</tr:argument>
    </tr:message>
  </tr:transaction>
</registry-response
```

### Key/Value format request (alternative wire format)

```
Version: 5.0
Action: chholder
CTID: cba-9345345321
Domain: de-example.de
Holder: DENIC-1000002-MAX
Generalrequest: DENIC-1000002-GENERAL
Abusecontact: DENIC-1000002-ABUSE
Nserver: ns1.xn--de-xample-x2a.de
Nserver: ns2.de-example.de 81.91.170.12
Nserver: ns2.de-example.de 2001:608:6:6:0:0:0:11
Dnskey: 257 3 8 AwEAAcoFUSyg1mkE5c33q8UbDiRZx5+/QtqFjVcyTEdv7YBYp9UnqrbXr7g4p8aDMI0ZuN4M8bxlPz+ItVfWO71rSkcxK1HwqmH4Pi1vSM3L6uYqZopEG9gJLqNpBBmzR29iSwR86TdnGUJ21Jfagc/+9xk3xmtdzNK3ROUcn/f8yiBN
```

### Key/Value format response

```
Result: success
STID: 74ba5119-74d1-4ba6-935f-4feb07ddd14d

Info: 53000080013 Domain "Status" is "connect"
Info: 16350000040 Verification information must be provided for the holder(s) to avoid dedelegation by [2024-12-09T15:45:01+01:00]
Info: 16350000041 Verification information must be provided for the holder(s) to avoid deletion by [2024-12-16T15:45:01+01:00]
STID: 57ebbb10-9590-11df-a9e2-9519b5688882
CTID: cba-9345345321
```

### Key/Value format response 2

```
Result: success
STID: 74ba5119-74d1-4ba6-935f-4feb07ddd14d

Info: 53000080015 Domain "Status" is "serverHold"
Info: 16350000041 Verification information must be provided for the holder(s) to avoid deletion by [2024-12-16T15:45:01+01:00]
STID: 57ebbb10-9590-11df-a9e2-9519b5688882
CTID: cba-9345345321
```
