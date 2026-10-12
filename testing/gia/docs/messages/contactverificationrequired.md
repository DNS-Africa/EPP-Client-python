# contactVerificationRequired

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-contactVerificationRequired.htm](https://docs.denic.de/en/Content/Beispiele/50/Message/MessageType-contactVerificationRequired.htm)

> Note: in the published example, the first `msg:message` closing tag is
> misspelled as `</msg:message>,` (comma instead of `>`). The live registry
> returns well-formed XML; treat this as a documentation typo, not a wire
> format feature.

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:queue-read msgType="contactVerificationRequired"/>
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
<msg:message xmlns:msg="http://registry.denic.de/msg/5.0" msgid="8960348c-6879-cb92-2b6f-cbc9abf98080" msgcnt="1" msgtime="2024-06-01T15:51:08+02:00">
  <msg:contactVerificationRequired>
    <msg:handle>DENIC-99995-BAD-GUY</msg:handle>
    <msg:verificationClaims>
      <msg:claim>name</msg:claim>
      <msg:claim>address</msg:claim>
    </msg:verificationClaims>
    <msg:numberOfReferencedDomainsTotal>2753</msg:numberOfReferencedDomainsTotal>
    <msg:earliestDomainForDedelegation>
      <msg:domain>
        <msg:handle>denic.de</msg:handle>
        <msg:ace>denic.de</msg:ace>
      </msg:domain>
      <msg:verificationDeadline>2024-06-06T15:51:08+02:00</msg:verificationDeadline>
      </msg:earliestDomainForDedelegation>
    <msg:earliestDomainForDeletion>
       <msg:domain>
         <msg:handle>denic.de</msg:handle>
         <msg:ace>denic.de</msg:ace>
       </msg:domain>
      <msg:verificationDeadline>2024-06-13T15:51:08+02:00</msg:verificationDeadline>
    </msg:earliestDomainForDeletion>
    <msg:message level="info" code="16350000050">
      <tr:text>Verification information must be provided for the handle to avoid dedelegation and/or deletion</tr:text>
    </msg:message>`,
    <msg:message level="info" code="16350000051">
      <tr:text>Please provide the requested verification information by means of a Contact UPDATE</tr:text>
    </msg:message>
  </msg:contactVerificationRequired>
</msg:message>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:msg="http://registry.denic.de/msg/5.0">
  <msg:delete msgid="02699380-9c7a-11de-8188-9ff72af94906" msgType="contactVerificationRequired"/>
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
Msgtype: contactVerificationRequired
```

### Key/Value format response

```
Result: success
STID: 253526e9-9f04-11df-a9e2-9519b5688882
Msgcnt: 1
Msgtime: 2024-06-01T15:51:08+02:00
Msgid: 8960348c-6879-cb92-2b6f-cbc9abf98080
msgtype: contactVerificationRequired
Handle: DENIC-99995-BAD-GUY
VerificationClaim: name
VerificationClaim: address
NumberOfReferencedDomainsTotal: 2753
Message: 16350000050 Verification information must be provided for the handle to avoid dedelegation and/or deletion
Message: 16350000051 Please provide the requested verification information by means of a Contact UPDATE

[earliest domain for dedelegation]
Domain: denic.de
Domain-ace: denic.de
VerificationDeadlineBeforeDedelegation: 2024-06-06T15:51:08+02:00

[earliest domain for deletion]
Domain: denic.de
Domain-ace: denic.de
VerificationDeadlineBeforeDeletion: 2024-06-13T15:51:08+02:00
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: queue-delete
Msgid: b988dae0-ae64-11de-b15c-f1279ab97beb
Msgtype: contactVerificationRequired
CTID: bre-34634621634
```

### Key/Value format response 2

```
Result: success
STID: 0b97f9b7-9f0b-11df-a9e2-9519b5688882
CTID: bre-34634621634
```
