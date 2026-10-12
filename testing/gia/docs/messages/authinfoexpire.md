# authInfoExpire

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-authInfoExpire.htm](https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-authInfoExpire.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:queue-read msgType="authInfoExpire"/>
</registry-request>
```

### XML response (queue-read, notification inside `<tr:data>`)

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>84272d50-9f0f-11df-a9e2-9519b5688882</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="02e4de03-9c7a-11de-8188-9ff72af94906" msgcnt="3" msgtime="2010-07-13T09:59:30+02:00">
        <msg:authInfoExpire>
          <msg:domain>
            <msg:handle>de-example.de</msg:handle>
            <msg:ace>de-example.de</msg:ace>
          </msg:domain>
          <msg:authinfoexpire>2010-08-12T00:00:00+02:00</msg:authinfoexpire>
        </msg:authInfoExpire>
      </msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:delete msgid="02699380-9c7a-11de-8188-9ff72af94906" msgType="authInfoExpire"/>
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
Msgtype: authinfoexpire
```

### Key/Value format response

```
Result: success
STID: d9058ba8-9f0b-11df-a9e2-9519b5688882
Msgcnt: 3
Msgtime: 2010-07-13T09:59:30+02:00
Msgid: 02e4de03-9c7a-11de-8188-9ff72af94906
Msgtype: authinfoexpire
Domain: de-example.de
Domain-ace: de-example.de
Authinfoexpire: 2010-08-12T00:00:00+02:00
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: queue-delete
Msgid: b988dae0-ae64-11de-b15c-f1279ab97beb
Msgtype: authinfoexpire
CTID: bre-34634621634
```

### Key/Value format response 2

```
Result: success
STID: 0b97f9b7-9f0b-11df-a9e2-9519b5688882
CTID: bre-34634621634
```
