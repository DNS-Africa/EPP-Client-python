# domainCREATE-AUTHINFO1

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/domainCREATE-AUTHINFO1.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/domainCREATE-AUTHINFO1.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:domain="http://registry.denic.de/domain/5.0">
  <domain:createAuthInfo1 hash="4213d924230224fd719218b4acbd92f96ebe4344f3d5d1478dede1aa44e4cf4b" expire="20100815">
    <domain:handle>de-example.de</domain:handle>
  </domain:createAuthInfo1>
  <ctid>987654321</ctid>
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
Action: create-authinfo1
Ctid: cba-987654321
Domain: de-example.de
Authinfohash: 4213d924230224fd719218b4acbd92f96ebe4344f3d5d1478dede1aa44e4cf4b
Authinfoexpire: 20100724
```

### Key/Value format response

```
Result: success
STID: 74ba5119-74d1-4ba6-935f-4feb07ddd14d

INFO: 53000080013 Domain "Status" is "connect"
INFO: 16350000040 Verification information must be provided for the holder(s) to avoid dedelegation by [2024-12-09T15:45:01+01:00]
INFO: 16350000041 Verification information must be provided for the holder(s) to avoid deletion by [2024-12-16T15:45:01+01:00]
Stid: 57ebbb10-9590-11df-a9e2-9519b5688882
Ctid: cba-9345345321
```

### Key/Value format response 2

```
Result: success
STID: 74ba5119-74d1-4ba6-935f-4feb07ddd14d

INFO: 53000080015 Domain "Status" is "serverHold"
INFO: 16350000041 Verification information must be provided for the holder(s) to avoid deletion by [2024-12-16T15:45:01+01:00]
Stid: 57ebbb10-9590-11df-a9e2-9519b5688882
Ctid: cba-9345345321
```
