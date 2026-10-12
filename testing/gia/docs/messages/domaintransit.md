# domainTransit

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-domainTransit.htm](https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-domainTransit.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:queue-read msgType="domainTransit"/>
</registry-request>
```

### XML response (queue-read, notification inside `<tr:data>`)

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>26bf1c3b-d742-4f20-8ce1-7e895f406205</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="f240fd12-ab5a-4219-8012-0136d0d047a9" msgcnt="1" msgtime="2025-08-06T09:35:06+02:00">
        <msg:domainTransit>
          <msg:domain>
            <msg:handle>example-domain.de</msg:handle>
            <msg:ace>example-domain.de</msg:ace>
          </msg:domain>
          <msg:message level="info" code="16350000032">
            <tr:text>Domain in Transit</tr:text>
            <tr:argument>request-reference DENIC#:1234</tr:argument>
          </msg:message>
        </msg:domainTransit>
      </msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:delete msgid="02699380-9c7a-11de-8188-9ff72af94906" msgType="domainTransit"/>
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
Msgtype: domainTransit
```

### Key/Value format response

```
Result: success
STID: c3b9e8d9-4466-4fc2-8a3b-156197820322

Msgcnt: 1
Msgtime: 2025-08-06T09:34:31+02:00
Msgid: 50e80b48-35dc-474a-9c4b-2e655a6d5f80
Msgtype: domainTransit
Domain: example-domain.de
Domain-ace: example-domain.de
Message: 16350000032 Domain in Transit [request-reference DENIC#:1234]
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: queue-delete
Msgid: b988dae0-ae64-11de-b15c-f1279ab97beb
Msgtype: domaintransit
CTID: bre-34634621634
```

### Key/Value format response 2

```
Result: success
STID: 0b97f9b7-9f0b-11df-a9e2-9519b5688882
CTID: bre-34634621634
```
