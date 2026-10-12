# domainDELETE

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/domainDELETE.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/domainDELETE.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:domain="http://registry.denic.de/domain/5.0">
  <domain:delete>
  <domain:handle>de-example.de</domain:handle>
  <domain:contact role="holder">DENIC-1000002-MAX</domain:contact>
  </domain:delete>
  <ctid>cba-987654321</ctid>
</registry-request>
```

### XML response

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>538f1687-963a-11df-a9e2-9519b5688882</tr:stid>
    <tr:ctid>cba-98765431</tr:ctid>
    <tr:result>success</tr:result>
  </tr:transaction>
</registry-response>
```

### Key/Value format request (alternative wire format)

```
Version: 5.0
Action: delete
CTID: cba-987654321
Domain: de-example.de
Holder: DENIC-1000002-MAX
```

### Key/Value format response

```
Result: success
STID: 1aba2fc0-9625-11df-a9e2-9519b5688882
CTID: cba-987654321
```
