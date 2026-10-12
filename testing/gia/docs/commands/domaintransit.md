# domainTRANSIT

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/domainTRANSIT.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/domainTRANSIT.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:domain="http://registry.denic.de/domain/5.0">
  <domain:transit disconnect="false">
  <domain:handle>de-example.de</domain:handle>
  </domain:transit>
  <ctid>cba-987654321</ctid>
</registry-request>
```

### XML response

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>342d1d01-963c-11df-a9e2-9519b5688882</tr:stid>
    <tr:ctid>cba-987654321</tr:ctid>
    <tr:result>success</tr:result>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:domain="http://registry.denic.de/domain/5.0">
  <domain:transit disconnect="true">
  <domain:handle>de-example.de</domain:handle>
  </domain:transit>
  <ctid>cba-987654321</ctid>
</registry-request>
```

### XML response 2

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>342d1d01-963c-11df-a9e2-9519b5688882</tr:stid>
    <tr:ctid>cba-987654321</tr:ctid>
    <tr:result>success</tr:result>
  </tr:transaction>
</registry-response>
```

### Key/Value format request (alternative wire format)

```
Version: 5.0
Action: transit
CTID: cba-987654321
Domain: de-example.de
Disconnect: false
```

### Key/Value format response

```
Result: success
STID: 1aba2fc0-9625-11df-a9e2-9519b5688882
CTID: cba-987654321
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: transit
CTID: cba-987654321
Domain: de-example.de
Disconnect: true
```

### Key/Value format response 2

```
Result: success
STID: 1aba2fc0-9625-11df-a9e2-9519b5688882
CTID: cba-987654321
```
