# domainCHECK

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/domainCHECK.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/domainCHECK.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:domain="http://registry.denic.de/domain/5.0">
  <domain:check>
    <domain:handle>de-example.de</domain:handle>
  </domain:check>
</registry-request>
```

### XML response

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>9e986503-9a2c-11df-a9e2-9519b5688882</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <domain:checkData xmlns:domain="http://registry.denic.de/domain/5.0">
        <domain:handle>test.de</domain:handle>
        <domain:status>connect</domain:status>
      </domain:checkData>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML response 2

```xml
<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>0a38e709-33e3-d5cf-cccf-622f9a16f225</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <domain:checkData xmlns:domain="http://registry.denic.de/domain/5.0">
        <domain:handle>de-example.de</domain:handle>
        <domain:ace>de-example.de</domain:ace>
        <domain:status>pendingCreate</domain:status>
      </domain:checkData>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML response 3

```xml
<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>0a38e709-33e3-d5cf-cccf-622f9a16f225</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <domain:checkData xmlns:domain="http://registry.denic.de/domain/5.0">
        <domain:handle>denic-server-hold.de</domain:handle>
        <domain:ace>denic-server-hold.de</domain:ace>
        <domain:status>serverHold</domain:status>
      </domain:checkData>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### Key/Value format request (alternative wire format)

```
Version: 5.0
Action: check
Domain: de-example.de
```

### Key/Value format response

```
Result: success
STID: 74ba5119-74d1-4ba6-935f-4feb07ddd14d

Domain: de-example.de
Status: exist
```

### Key/Value format response 2

```
Result: success
STID: 74ba5119-74d1-4ba6-935f-4feb07ddd14d

Domain: de-example.de
Domain-Ace: de-example.de
Status: pendigCreate
```

### Key/Value format response 3

```
Result: success
STID: 74ba5119-74d1-4ba6-935f-4feb07ddd14d

Domain: de-example.de
Domain-Ace: de-example.de
Status: serverHold
```
