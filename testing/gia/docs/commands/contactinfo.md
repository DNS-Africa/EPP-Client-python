# contactINFO

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/contactINFO.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/contactINFO.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:contact="http://registry.denic.de/contact/5.0" xmlns:verification="http://registry.denic.de/verification/5.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <contact:info>
    <contact:handle>DENIC-1000022-EXAMPLE-XML-PERSON</contact:handle>
  </contact:info>
</registry-request>
```

### XML response

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>b61d054e-d751-4c96-a180-c2eb4230a374</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <contact:infoData xmlns:contact="http://registry.denic.de/contact/5.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
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
        <contact:changed>2024-09-27T16:40:53+02:00</contact:changed>
        <verification:verificationInformation xmlns:verification="http://registry.denic.de/verification/5.0" xsi:type="verification:verificationInformationType">
          <verification:verifiedClaims>
            <verification:claim>address</verification:claim>
            <verification:claim>name</verification:claim>
          </verification:verifiedClaims>
          <verification:verificationResult>success</verification:verificationResult>
          <verification:verificationReference>ABC123/45GHT</verification:verificationReference>
          <verification:verificationTimestamp>2023-11-11T14:36:21+01:00</verification:verificationTimestamp>
          <verification:verificationEvidence>idcard</verification:verificationEvidence>
          <verification:verificationMethod>auth</verification:verificationMethod>
          <verification:trustFramework>de_denic</verification:trustFramework>
        </verification:verificationInformation>
      </contact:infoData>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### Key/Value format request (alternative wire format)

```
Version: 5.0
Action: INFO
Handle: DENIC-1000022-EXAMPLE-PERSON
```

### Key/Value format response

```
RESULT: success
STID: 8e9ccb16-f362-4eb3-9428-763bae69705b

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
Changed: 2024-09-27T16:38:17+02:00

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
