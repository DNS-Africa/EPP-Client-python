# expire

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-expire.htm](https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-expire.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:queue-read msgType="expire"/>
</registry-request>
```

### XML response (queue-read, notification inside `<tr:data>`)

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>bb3845ca-9f0e-11df-a9e2-9519b5688882</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="0295ac91-9c7a-11de-8188-9ff72af94906" msgcnt="7" msgtime="2010-07-05T16:37:50+02:00">
        <msg:expire>
          <msg:domain>
            <msg:handle>de-example.de</msg:handle>
            <msg:ace>de-example.de</msg:ace>
            <msg:expire>2010-07-07T16:37:50+02:00</msg:expire>
          </msg:domain>
        </msg:expire>
      </msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:delete msgid="02699380-9c7a-11de-8188-9ff72af94906" msgType="expire"/>
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
Msgtype: expire
```

### Key/Value format response

```
Result: success
STID: 78bf488c-9f0c-11df-a9e2-9519b5688882
Msgcnt: 7
Msgtime: 2010-07-05T16:37:50+02:00
Msgid: 0295ac91-9c7a-11de-8188-9ff72af94906
Msgtype: expire
Domain: de-example.de
Domain-ace: de-example.de
Expire: 2010-07-07T16:37:50+02:00
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: queue-delete
Msgid: b988dae0-ae64-11de-b15c-f1279ab97beb
Msgtype: expire
CTID: bre-34634621634
```

### Key/Value format response 2

```
Result: success
STID: 0b97f9b7-9f0b-11df-a9e2-9519b5688882
CTID: bre-34634621634
```
