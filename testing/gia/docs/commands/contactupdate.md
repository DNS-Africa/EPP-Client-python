# contactUPDATE

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/contactUPDATE.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/contactUPDATE.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:contact="http://registry.denic.de/contact/5.0" xmlns:verification="http://registry.denic.de/verification/5.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <contact:update>
    <contact:handle>DENIC-1000022-EXAMPLE-XML-PERSON</contact:handle>
    <contact:type>PERSON</contact:type>
    <contact:name>John Doe</contact:name>
    <contact:organisation>DENIC eG</contact:organisation>
    <contact:postal>
      <contact:address>Theodor-Stern-Kai 1</contact:address>
      <contact:postalCode>60596</contact:postalCode>
      <contact:city>Frankfurt am Main</contact:city>
      <contact:countryCode>DE</contact:countryCode>
    </contact:postal>
    <contact:email>john.doe@denic.de</contact:email>
    <contact:phone>+49.69272350</contact:phone>
    <verification:verificationInformation xmlns:verification="http://registry.denic.de/verification/5.0" xsi:type="verification:verificationInformationType">
       <verification:verifiedClaims>
        <verification:claim>name</verification:claim>
        <verification:claim>address</verification:claim>
      </verification:verifiedClaims>
      <verification:verificationResult>success</verification:verificationResult>
      <verification:verificationReference>ABC123/45GHT</verification:verificationReference>
      <verification:verificationTimestamp>2023-11-11T15:36:21+02:00</verification:verificationTimestamp>
      <verification:verificationEvidence>idcard</verification:verificationEvidence>
      <verification:verificationMethod>auth</verification:verificationMethod>
      <verification:trustFramework>de_denic</verification:trustFramework>
    </verification:verificationInformation>
  </contact:update>
  <ctid>xml-74ba5118</ctid>
</registry-request>
```

### XML response

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>25cf1349-dfb4-48e9-951c-af60b068ba24</tr:stid>
    <tr:ctid>xml-74ba5118</tr:ctid>
    <tr:result>success</tr:result>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="https://registry.denic.de/global/5.0" xmlns:contact="https://registry.denic.de/contact/5.0">
  <contact:update>
    <contact:handle>DENIC-99995-GENREQ</contact:handle>
    <contact:type>REQUEST</contact:type>
    <contact:uri-template>https://denic.de/contact/form{?Alabel,Ulabel}</contact:uritemplate>
  </contact:update>
  <ctid>cba-987654321</ctid>
</registry-request>
```

### XML response 2

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>bb135322-958c-11df-a9e2-9519b5688882</tr:stid>
    <tr:ctid>cba-987654321</tr:ctid>
    <tr:result>success</tr:result>
  </tr:transaction>
</registry-response>
```

### Key/Value format request (alternative wire format)

```
Version: 5.0
Action: CREATE
Handle: DENIC-1000022-EXAMPLE-PERSON
Type: PERSON
Organisation: DENIC eG
Name: Max Mustermann
Address: Business Services
Address: Theodor-Stern-Kai 1
Address: in Frankfurt
Address: south side
Address: riverside
PostalCode: 60596
City: Frankfurt am Main
CountryCode: DE
eMail: email-1@denic.de
eMail: email-2@denic.de
eMail: email-3@denic.de
eMail: email-4@denic.de
eMail: email-5@denic.de
eMail: email-6@denic.de
Phone: +49.6927235x290
CTID: kv-7bf04fa8

[VerificationInformation]
VerifiedClaim: name
VerifiedClaim: address
VerificationResult: success
VerificationReference: ABC123/45GHT
VerificationTimestamp: 2023-11-11T15:36:21+02:00
VerificationEvidence: idcard
VerificationMethod: auth
TrustFramework: de_denic

[VerificationInformation]
VerifiedClaim: email
VerificationResult: failed
VerificationReference: 354546TZQ
VerificationTimestamp: 2023-10-04T12:22:19+02:00
VerificationEvidence: email_ver_transaction_log
VerificationMethod: reachability
TrustFramework: de_denic
```

### Key/Value format response

```
RESULT: success
STID: c5f61739-600d-4c3c-b0a7-058bf8254aa7
CTID: kv-7bf04fa8
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: update
Type: request
Handle: DENIC-99995-GENREQ
Uri-template: https://denic.de/contact/form{?Alabel,Ulabel}
```

### Key/Value format response 2

```
Result: success
STID: 4cfcf3ff-958c-11df-a9e2-9519b5688882
```
