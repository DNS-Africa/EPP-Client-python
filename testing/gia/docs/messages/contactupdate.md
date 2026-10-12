# contactUpdate

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-contactUpdate.htm](https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-contactUpdate.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:queue-read msgType="contactUpdate"/>
</registry-request>
```

### XML response (queue-read, notification inside `<tr:data>`)

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>e5b905e9-f867-4fcd-8e93-e13db4ff3065</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="437275c2-17bc-4c21-9cba-dec059db5cb6" msgcnt="1" msgtime="2025-08-06T09:31:19+02:00">
        <msg:contactUpdate>
          <msg:contact>
            <msg:handle>DENIC-1000021-A8WKXH0L3T</msg:handle>
          </msg:contact>
          <msg:message level="info" code="16350000041">
            <tr:text>Contact has been updated - please check contact data with RRI-INFO command</tr:text>
            <tr:argument>request-reference DENIC#:1234</tr:argument>
          </msg:message>
          <msg:message level="info" code="16350000042">
            <tr:text>Contact update impacts all referenced domains</tr:text>
          </msg:message>
        </msg:contactUpdate>
      </msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:delete msgid="02699380-9c7a-11de-8188-9ff72af94906" msgType="contactDelete"/>
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
Msgtype: contactupdate
```

### Key/Value format response

```
Result: success
STID: 3ebce664-77c3-11e0-921c-0d6566ad5b9b
Msgcnt: 1
Msgtime: 2011-05-06T11:18:10+02:00
Msgid: c309127b-77c1-11e0-8d67-6bfe298a2a5f
Msgtype: contactupdate
contact: DENIC-1000021-L7OCX8HTY8
Message: 13000000041 Contact has been updated - please check contact data with RRI-INFO command [request-reference DENIC#:1234]
Message: 13000000042 Contact update impacts all referenced domains
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: queue-delete
Msgid: b988dae0-ae64-11de-b15c-f1279ab97beb
Msgtype: contactUpdate
CTID: bre-34634621634
```

### Key/Value format response 2

```
Result: success
STID: 0b97f9b7-9f0b-11df-a9e2-9519b5688882
CTID: bre-34634621634
```
