# lockDelete

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-lockDelete.htm](https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-lockDelete.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
    <msg:queue-read msgType="lockDelete"/>
</registry-request>
```

### XML response (queue-read, notification inside `<tr:data>`)

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>48d8eec1-12bc-490c-9d27-95e4835ffc58</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="b5929ad9-d2da-4c0f-96a5-319c9f028c95" msgcnt="1" msgtime="2025-08-06T09:44:59+02:00">
        <msg:lockDelete>
          <msg:domain>
            <msg:handle>example-domain.de</msg:handle>
            <msg:ace>example-domain.de</msg:ace>
          </msg:domain>
          <msg:message level="info" code="13000000041">
            <tr:text>Domain has been unlocked</tr:text>
            <tr:argument>request-reference DENIC#:1234</tr:argument>
          </msg:message>
        </msg:lockDelete>
      </msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
    <msg:delete msgid="c36a642b-1f71-44c9-b55d-2f9be29c3c48" msgType="lockDelete"/>
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
Action: QUEUE-READ
Msgtype: lockdelete
```

### Key/Value format response

```
Result: success
STID: a01d52ca-479a-4b7d-af83-016a02ac74e9
Msgcnt: 1
Msgtime: 2025-08-06T09:44:15+02:00
Msgid: b6336b10-f5f0-4a3b-bf94-387088499436
Msgtype: lockDelete
Domain: example-domain.de
Domain-ace: example-domain.de
Message: 13000000041 Domain has been unlocked [request-reference DENIC#:1234]
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: queue-delete
Msgid: e6fc98ab-6e32-4ae4-8554-6157aaf148a4
Msgtype: lockdelete
```

### Key/Value format response 2

```
Result: success
STID: 0b97f9b7-9f0b-11df-a9e2-9519b5688882
CTID: bre-34634621634
```
