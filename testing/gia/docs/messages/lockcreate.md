# lockCreate

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-lockCreate.htm](https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-lockCreate.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
    <msg:queue-read msgType="lockCreate"/>
</registry-request>
```

### XML response (queue-read, notification inside `<tr:data>`)

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>5ddb3dd3-43cc-4c54-9fe0-21af54a20108</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="5be27a39-dc47-452e-b826-1b4cbf4be386" msgcnt="1" msgtime="2025-08-06T09:41:48+02:00">
        <msg:lockCreate>
          <msg:domain>
            <msg:handle>example-domain.de</msg:handle>
            <msg:ace>example-domain.de</msg:ace>
          </msg:domain>
          <msg:message level="info" code="13000000040">
            <tr:text>Domain has been locked</tr:text>
            <tr:argument>request-reference DENIC#:1234</tr:argument>
          </msg:message>
        </msg:lockCreate>
      </msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
    <msg:delete msgid="60d1d81c-a4e6-49eb-9d08-b5a46c0c994c" msgType="lockCreate"/>
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
Msgtype: lockcreate
```

### Key/Value format response

```
Result: success
STID: 7db73fdf-5bb4-4e83-82d6-60bc0ee0a958
Msgcnt: 1
Msgtime: 2025-08-06T09:41:17+02:00
Msgid: eec82155-700e-471c-ac57-97478d6be202
Msgtype: lockCreate
Domain: example-domain.de
Domain-ace: example-domain.de
message: 13000000040 Domain has been locked [request-reference DENIC#:1234]
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: queue-delete
msgid: ea83be67-4637-4b30-8d48-5ea8782f0b0c
msgtype: lockcreate
```

### Key/Value format response 2

```
Result: success
STID: 0b97f9b7-9f0b-11df-a9e2-9519b5688882
CTID: bre-34634621634
```
