# contactCHECK

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/contactCHECK.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/contactCHECK.htm)

### XML request

```xml
<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:contact="http://registry.denic.de/contact/5.0">
  <contact:check>
    <contact:handle>DENIC-1000002-MAX</contact:handle>
  </contact:check>
</registry-request>
```

### XML response

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>ba1b8093-9a2b-11df-a9e2-9519b5688882</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <contact:checkData xmlns:contact="http://registry.denic.de/contact/5.0">
        <contact:handle>DENIC-1000002-MAX</contact:handle>
        <contact:status>exist</contact:status>
      </contact:checkData>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### Key/Value format request (alternative wire format)

```
Version: 5.0
Action: check
Handle: DENIC-1000002-MAX
```

### Key/Value format response

```
Result: success
STID: 74ba5119-74d1-4ba6-935f-4feb07ddd14d

Handle: DENIC-1000002-MAX
Status: exist
```
