# domainUpdate

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-domainUpdate.htm](https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-domainUpdate.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
    <msg:queue-read msgType="domainUpdate"/>
</registry-request>
```

### XML response (queue-read, notification inside `<tr:data>`)

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>326a9285-0324-4fb5-bc35-ed0f4e34d1c5</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="c7e72b9d-666e-4bcb-9f4e-8265f19a2a8c" msgcnt="1" msgtime="2025-08-06T09:39:05+02:00">
        <msg:domainUpdate>
          <msg:domain>
            <msg:handle>example-domain.de</msg:handle>
            <msg:ace>example-domain.de</msg:ace>
          </msg:domain>
          <msg:message level="info" code="16350000030">
            <tr:text>Domain has been updated - please check domain data with RRI-INFO command</tr:text>
            <tr:argument>request-reference DENIC#:1234</tr:argument>
          </msg:message>
        </msg:domainUpdate>
      </msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
    <msg:delete msgid="665ffa8b-b288-45e9-a8d2-f46baa581226" msgType="domainUpdate"/>
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
Msgtype: domainupdate
```

### Key/Value format response

```
Result: success
STID: c2ee8611-5f6f-4d2a-a469-0908b484ffa6

Msgcnt: 1
Msgtime: 2025-08-06T09:38:17+02:00
Msgid: 93505557-58c8-4fef-aa6c-e038fba7fd1f
Msgtype: domainUpdate
Domain: example-domain.de
Domain-ace: example-domain.de
Message: 16350000030 Domain has been updated - please check domain data with RRI-INFO command [request-reference DENIC#:1234]
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: queue-delete
Msgid: 126ada09-cf2d-4f96-bdf2-c46cdc8007f7
Msgtype: domainUpdate
```

### Key/Value format response 2

```
Result: success
STID: 0b97f9b7-9f0b-11df-a9e2-9519b5688882
CTID: bre-34634621634
```
