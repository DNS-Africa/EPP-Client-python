# authInfo2Delete

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-authInfo2Delete.htm](https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-authInfo2Delete.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:queue-read msgType="authInfo2Delete"/>
</registry-request>
```

### XML response (queue-read, notification inside `<tr:data>`)

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>5546aa50-77c2-11e0-921c-0d6566ad5b9b</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="c309127b-77c1-11e0-8d67-6bfe298a2a5f" msgcnt="1" msgtime="2011-05-06T11:18:10+02:00">
        <msg:authInfo2Delete>
          <msg:domain>
            <msg:handle>de-domain.de</msg:handle>
            <msg:ace>de-domain.de</msg:ace>
          </msg:domain>
          <msg:message level="info" code="11300088725">
            <tr:text>AuthInfo deleted</tr:text>
          </msg:message>
          <msg:message level="info" code="11300088726">
            <tr:text>AuthInfo letter could not be delivered</tr:text>
          </msg:message>
        </msg:authInfo2Delete>
      </msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:delete msgid="02699380-9c7a-11de-8188-9ff72af94906" msgType="authInfo2Delete"/>
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
Msgtype: authinfo2delete
```

### Key/Value format response

```
Result: success
STID: 3ebce664-77c3-11e0-921c-0d6566ad5b9b
Msgcnt: 1
Msgtime: 2011-05-06T11:18:10+02:00
Msgid: c309127b-77c1-11e0-8d67-6bfe298a2a5f
Msgtype: authinfo2delete
Domain: de-example.de
Domain-ace: de-example.de
Message: 11300077725 AuthInfo deleted
Message: 11300077726 AuthInfo letter could not be delivered
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: queue-delete
Msgid: b988dae0-ae64-11de-b15c-f1279ab97beb
Msgtype: authinfo2delete
CTID: bre-34634621634
```

### Key/Value format response 2

```
Result: success
STID: 0b97f9b7-9f0b-11df-a9e2-9519b5688882
CTID: bre-34634621634
```
