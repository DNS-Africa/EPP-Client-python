# domainStatusUpdate

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-domainStatusUpdate.htm](https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-domainStatusUpdate.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:queue-read msgType="domainStatusUpdate"/>
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
<msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="8960348c-6879-cb92-2b6f-cbc9abf91616" msgcnt="1" msgtime="2024-06-01T15:51:08+02:00">
  <msg:domainStatusUpdate>
    <msg:domain>
      <msg:handle>de-example.de</msg:handle>
      <msg:ace>de-example.de</msg:ace>
    </msg:domain>
    <msg:holders>
      <msg:handle>DENIC-1000002-GoodGuy</msg:handle>
      <msg:handle>DENIC-1000002-GoodGuy2</msg:handle>
    </msg:holders>
    <msg:status>connect</msg:status>
  </msg:domainStatusUpdate>
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
<msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="8960348c-6879-cb92-2b6f-cbc9abf91616" msgcnt="1" msgtime="2024-06-01T15:51:08+02:00">
  <msg:domainStatusUpdate>
    <msg:domain>
      <msg:handle>de-example.de</msg:handle>
      <msg:ace>de-example.de</msg:ace>
    </msg:domain>
    <msg:holders>
      <msg:handle>DENIC-1000002-MaybeGoodGuy</msg:handle>
      <msg:handle>DENIC-1000002-GoodGuy</msg:handle>
    </msg:holders>
    <msg:status>connect</msg:status>
    <msg:verificationDeadlineBeforeDedelegation>2024-06-06T15:51:08+02:00</msg:verificationDeadlineBeforeDedelegation>
    <msg:verificationDeadlineBeforeDeletion>2024-06-13T15:51:08+02:00</msg:verificationDeadlineBeforeDeletion>
    <msg:message level="info" code="16350000040">
      <tr:text>Verification information must be provided for the holder(s) to avoid dedelegation by</tr:text>
        <tr:argument>Date: 2024-06-06T15:51:08+02:00</tr:argument>
        <tr:argument>VerificationClaims: address;name</tr:argument>
     </msg:message>
    <msg:verificationDeadlineBeforeDeletion>2024-06-13T15:51:08+02:00</msg:verificationDeadlineBeforeDeletion>
    <msg:message level="info" code="16350000041">
      <tr:text>Verification information must be provided for the holder(s) to avoid deletion by</tr:text>
      <tr:argument>Date: 2024-06-13T15:51:08+02:00</tr:argument>
      <tr:argument>VerificationClaims: address;name</tr:argument>
    </msg:message>
   </msg:domainStatusUpdate>
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
<msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="8960348c-6879-cb92-2b6f-cbc9abf91616" msgcnt="1" msgtime="2024-06-01T15:51:08+02:00">
  <msg:domainStatusUpdate>
    <msg:domain>
      <msg:handle>de-example.de</msg:handle>
      <msg:ace>de-example.de</msg:ace>
    </msg:domain>
    <msg:holders>
      <msg:handle>DENIC-1000002-BadGuy</msg:handle>
      <msg:handle>DENIC-1000002-GoodGuy</msg:handle>
    </msg:holders>
    <msg:status>serverHold</msg:status>
    <msg:verificationDeadlineBeforeDeletion>2024-06-13T15:51:08+02:00</msg:verificationDeadlineBeforeDeletion>
    <msg:message level="info" code="16350000041">
      <tr:text>Verification information must be provided for the holder(s) to avoid deletion by</tr:text>
      <tr:argument>Date: 2024-06-13T15:51:08+02:00</tr:argument>
      <tr:argument>VerificationClaims: address;name</tr:argument>
    </msg:message>
   </msg:domainStatusUpdate>
</msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:delete msgid="02699380-9c7a-11de-8188-9ff72af94906" msgType="domainStatusUpdate"/>
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
Msgtype: domainstatusupdate
```

### Key/Value format response

```
Result: success
STID: 78bf488c-9f0c-11df-a9e2-9519b5688882
Msgcnt: 1
Msgtime: 2024-06-01T15:51:08+02:00
Msgid: 8960348c-6879-cb92-2b6f-cbc9abf91616
Msgtype: domainStatusUpdate
Domain: de-example.de
Domain-ace: de-example.de
Holder: DENIC-1000002-GoodGuy
Holder: DENIC-1000002-GoodGuy2
Status: connect
```

### Key/Value format response 2

```
Result: success
STID: 78bf488c-9f0c-11df-a9e2-9519b5688882
Msgcnt: 1
Msgtime: 2024-06-01T15:51:08+02:00
Msgid: 8960348c-6879-cb92-2b6f-cbc9abf91616
Msgtype: domainStatusUpdate
Domain: de-example.de
Domain-ace: de-example.de
Holder: DENIC-1000002-MaybeGoodGuy
Holder: DENIC-1000002-GoodGuy
Status: connect
VerificationDeadlineBeforeDedelegation: 2024-06-06T15:51:08+02:00
VerificationDeadlineBeforeDeletion: 2024-06-13T15:51:08+02:00
Message: 16350000040 Verification information must be provided for the holder(s) to avoid dedelegation by [Date: 2024-06-06T15:51:08+02:00, VerificationClaims: address;name]
Message: 16350000041 Verification information must be provided for the holder(s) to avoid deletion by [Date: 2024-06-13T15:51:08+02:00, VerificationClaims: address;name]
```

### Key/Value format response 3

```
Result: success
STID: 78bf488c-9f0c-11df-a9e2-9519b5688882
Msgcnt: 1
Msgtime: 2024-06-01T15:51:08+02:00
Msgid: 8960348c-6879-cb92-2b6f-cbc9abf91616
Msgtype: domainStatusUpdate
Domain: de-example.de
Domain-ace: de-example.de
Holder: DENIC-1000002-BadGuy
Holder: DENIC-1000002-GoodGuy
Status: serverHold
VerificationDeadlineBeforeDeletion: 2024-06-13T15:51:08+02:00
Message: 16350000041 Verification information must be provided for the holder(s) to avoid deletion by [Date: 2024-06-13T15:51:08+02:00, VerificationClaims: address;name]
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
