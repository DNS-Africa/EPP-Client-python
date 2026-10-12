# domainDelete

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-domainDelete.htm](https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-domainDelete.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:queue-read msgType="domainDelete"/>
</registry-request>
```

### XML response (queue-read, notification inside `<tr:data>`)

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>ae029b0a-50af-11e0-b375-95a6041ce317</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="ee6bfa7f-4afd-11e0-ad4b-47ecb35e56d2" msgcnt="1" msgtime="2011-03-10T11:05:30+01:00">
        <msg:domainDelete>
          <msg:domain>
            <msg:handle>de-domain.de</msg:handle>
            <msg:ace>de-domain.de</msg:ace>
          </msg:domain>
          <msg:message level="info" code="16350000031">
            <tr:text>Domain has been deleted</tr:text>
            <tr:argument>request-reference DENIC#:2011031043000000</tr:argument>
          </msg:message>
        </msg:domainDelete>
      </msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML response (queue-read, notification inside `<tr:data>`) (2)

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>ae029b0a-50af-11e0-b375-95a6041ce317</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
<msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="8960348c-6879-cb92-2b6f-cbc9abf98080" msgcnt="1" msgtime="2024-06-01T15:51:08+02:00">
  <msg:domainDelete>
    <msg:domain>
      <msg:handle>de-example.de</msg:handle>
      <msg:ace>de-example.de</msg:ace>
    </msg:domain>
    <msg:message level="info" code="16350000031">
      <tr:text>Domain has been deleted</tr:text>
      <tr:argument>no verification information provided</tr:argument>
    </msg:message>
  </msg:domainDelete>
</msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML response (queue-read, notification inside `<tr:data>`) (3)

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>ae029b0a-50af-11e0-b375-95a6041ce317</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
<msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="8960348c-6879-cb92-2b6f-cbc9abf98080" msgcnt="1" msgtime="2024-06-01T15:51:08+02:00">
  <msg:domainDelete>
    <msg:domain>
      <msg:handle>de-example.de</msg:handle>
      <msg:ace>de-example.de</msg:ace>
    </msg:domain>
    <msg:message level="info" code="16350000031">
      <tr:text>Domain has been deleted</tr:text>
      <tr:argument>request-reference DENIC#:2024100143000000</tr:argument>
    </msg:message>
  </msg:domainDelete>
</msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:delete msgid="02699380-9c7a-11de-8188-9ff72af94906" msgType="domainDelete"/>
</registry-request>
```

### XML response

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>078db1bf-9f0a-11df-a9e2-9519b5688882</tr:stid>
    <tr:result>success</tr:result>
  </tr:transaction>
</registry-response>
```

### Key/Value format request (alternative wire format)

```
Version: 5.0
Action: queue-read
Msgtype: domaindelete
```

### Key/Value format response

```
Result: success
STID: 78bf488c-9f0c-11df-a9e2-9519b5688882
Msgcnt: 1
Msgtime: 2011-03-10T11:05:30+01:00
Msgid: ee6bfa7f-4afd-11e0-ad4b-47ecb35e56d2
Msgtype: domainDelete
Domain: de-example.de
Domain-ace: de-example.de
Message: 16350000031 Domain has been deleted []
```

### Key/Value format response 2

```
Result: success
STID: 253526e9-9f04-11df-a9e2-9519b5688882
Msgcnt: 1
Msgtime: 2024-06-01T15:51:08+02:00
Msgid: 8960348c-6879-cb92-2b6f-cbc9abf98080
Msgtype: domainDelete
Domain: de-example.de
Domain-ace: de-example.de
Message: 16350000031 Domain has been deleted [no verification information provided]
```

### Key/Value format response 3

```
Result: success
STID: 253526e9-9f04-11df-a9e2-9519b5688882
Msgcnt: 1
Msgtime: 2024-06-01T15:51:08+02:00
Msgid: 8960348c-6879-cb92-2b6f-cbc9abf98080
Msgtype: domainDelete
Domain: de-example.de
Domain-ace: de-example.de
Message: 16350000031 Domain has been deleted [request-reference DENIC#:2024100143000000]
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: queue-delete
Msgid: b988dae0-ae64-11de-b15c-f1279ab97beb
Msgtype: domainDelete
CTID: bre-34634621634
```

### Key/Value format response 4

```
Result: success
STID: 0b97f9b7-9f0b-11df-a9e2-9519b5688882
CTID: bre-34634621634
```
