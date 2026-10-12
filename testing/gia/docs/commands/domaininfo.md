# domainINFO

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/domainINFO.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/domainINFO.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:domain="http://registry.denic.de/domain/5.0">
   <domain:info recursive="false">
      <domain:handle>domain-example-1000022.de</domain:handle>
   </domain:info>
</registry-request>
```

### XML response

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>8a62923d-89f9-4fc7-9852-2bec74b5a1f9</tr:stid>
    <tr:result>success</tr:result>
    <tr:message level="info" code="13000000011">
      <tr:text>Request was processed in test environment - not valid in real world</tr:text>
      <tr:argument>testing platform</tr:argument>
    </tr:message>
    <tr:data>
      <domain:infoData xmlns:domain="http://registry.denic.de/domain/5.0" xmlns:contact="http://registry.denic.de/contact/5.0" xmlns:dnsentry="http://registry.denic.de/dnsentry/5.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <domain:handle>domain-example-1000022.de</domain:handle>
        <domain:ace>domain-example-1000022.de</domain:ace>
        <domain:status>pendingCreate</domain:status>
        <domain:contact role="generalrequest"/>
        <domain:contact role="abusecontact"/>
        <domain:contact role="holder"/>
        <dnsentry:dnsentry xsi:type="dnsentry:A">
          <dnsentry:owner>domain-example-1000022.de.</dnsentry:owner>
          <dnsentry:rdata>
            <dnsentry:address>127.0.0.1</dnsentry:address>
          </dnsentry:rdata>
        </dnsentry:dnsentry>
        <domain:registrationDate>2024-10-04T13:31:25+02:00</domain:registrationDate>
        <domain:changed>2024-10-04T18:23:08+02:00</domain:changed>
        <domain:regAcc>
          <domain:regAccId>DENIC-1000022</domain:regAccId>
          <domain:name>DENIC eG</domain:name>
        </domain:regAcc>
      </domain:infoData>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML response 2

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>e742d307-dd8b-41dc-8fc1-3db0ff50a5b9</tr:stid>
    <tr:result>success</tr:result>
    <tr:message level="info" code="13000000011">
      <tr:text>Request was processed in test environment - not valid in real world</tr:text>
      <tr:argument>testing platform</tr:argument>
    </tr:message>
    <tr:data>
      <domain:infoData xmlns:domain="http://registry.denic.de/domain/5.0" xmlns:contact="http://registry.denic.de/contact/5.0" xmlns:dnsentry="http://registry.denic.de/dnsentry/5.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <domain:handle>domain-example-1000022.de</domain:handle>
        <domain:ace>domain-example-1000022.de</domain:ace>
        <domain:status>pendingCreate</domain:status>
        <domain:contact role="generalrequest">
          <contact:handle>DENIC-1000022-EXAMPLE-GR</contact:handle>
        </domain:contact>
        <domain:contact role="abusecontact">
          <contact:handle>DENIC-1000022-EXAMPLE-ABUSE</contact:handle>
        </domain:contact>
        <domain:contact role="holder">
          <contact:handle>DENIC-1000022-EXAMPLE-ORG</contact:handle>
        </domain:contact>
        <domain:contact role="holder">
          <contact:handle>DENIC-1000022-EXAMPLE-PERSON</contact:handle>
        </domain:contact>
        <dnsentry:dnsentry xsi:type="dnsentry:A">
          <dnsentry:owner>domain-example-1000022.de.</dnsentry:owner>
          <dnsentry:rdata>
            <dnsentry:address>127.0.0.1</dnsentry:address>
          </dnsentry:rdata>
        </dnsentry:dnsentry>
        <domain:registrationDate>2024-10-04T13:31:25+02:00</domain:registrationDate>
        <domain:changed>2024-10-04T18:23:08+02:00</domain:changed>
        <domain:regAcc>
          <domain:regAccId>DENIC-1000022</domain:regAccId>
          <domain:name>DENIC eG</domain:name>
        </domain:regAcc>
      </domain:infoData>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 2

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:domain="http://registry.denic.de/domain/5.0">
   <domain:info recursive="false">
      <domain:handle>domain-example-1000022.de</domain:handle>
      <domain:authInfo>My-Very-Secret-Auth-Info</domain:authInfo>
   </domain:info>
</registry-request>
```

### XML response 3

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>1f33a361-e9c0-4776-a59f-167305200898</tr:stid>
    <tr:result>success</tr:result>
    <tr:message level="info" code="13000000011">
      <tr:text>Request was processed in test environment - not valid in real world</tr:text>
      <tr:argument>testing platform</tr:argument>
    </tr:message>
    <tr:data>
      <domain:infoData xmlns:domain="http://registry.denic.de/domain/5.0" xmlns:contact="http://registry.denic.de/contact/5.0" xmlns:dnsentry="http://registry.denic.de/dnsentry/5.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <domain:handle>domain-example-1000022.de</domain:handle>
        <domain:ace>domain-example-1000022.de</domain:ace>
        <domain:status>pendingCreate</domain:status>
        <domain:authInfo>true</domain:authInfo>
        <domain:contact role="generalrequest"/>
        <domain:contact role="abusecontact"/>
        <domain:contact role="holder"/>
        <dnsentry:dnsentry xsi:type="dnsentry:A">
          <dnsentry:owner>domain-example-1000022.de.</dnsentry:owner>
          <dnsentry:rdata>
            <dnsentry:address>127.0.0.1</dnsentry:address>
          </dnsentry:rdata>
        </dnsentry:dnsentry>
        <domain:registrationDate>2024-10-04T13:31:25+02:00</domain:registrationDate>
        <domain:changed>2024-10-04T18:23:08+02:00</domain:changed>
        <domain:regAcc>
          <domain:regAccId>DENIC-1000022</domain:regAccId>
          <domain:name>DENIC eG</domain:name>
        </domain:regAcc>
      </domain:infoData>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 3

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:domain="http://registry.denic.de/domain/5.0">
   <domain:info recursive="true">
      <domain:handle>domain-example-1000022.de</domain:handle>
   </domain:info>
</registry-request>
```

### XML response 4

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>d0dccb85-2d39-4ebb-8f7c-92f55f1de7b1</tr:stid>
    <tr:result>success</tr:result>
    <tr:message level="info" code="13000000011">
      <tr:text>Request was processed in test environment - not valid in real world</tr:text>
      <tr:argument>testing platform</tr:argument>
    </tr:message>
    <tr:data>
      <domain:infoData xmlns:domain="http://registry.denic.de/domain/5.0" xmlns:contact="http://registry.denic.de/contact/5.0" xmlns:dnsentry="http://registry.denic.de/dnsentry/5.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <domain:handle>domain-example-1000022.de</domain:handle>
        <domain:ace>domain-example-1000022.de</domain:ace>
        <domain:status>pendingCreate</domain:status>
        <domain:contact role="generalrequest">
          <contact:type>REQUEST</contact:type>
          <contact:uri-template>mailto:://noreply@denic.de</contact:uri-template>
          <contact:changed>2024-10-04T13:21:16+02:00</contact:changed>
        </domain:contact>
        <domain:contact role="abusecontact">
          <contact:type>REQUEST</contact:type>
          <contact:uri-template>mailto:://noreply@denic.de</contact:uri-template>
          <contact:changed>2024-10-04T13:21:25+02:00</contact:changed>
        </domain:contact>
        <domain:contact role="holder">
          <contact:type>ORG</contact:type>
          <contact:name>DENIC eG</contact:name>
          <contact:postal>
            <contact:address>Theodor-Stern-Kai 1</contact:address>
            <contact:postalCode>60596</contact:postalCode>
            <contact:city>Frankfurt</contact:city>
            <contact:countryCode>DE</contact:countryCode>
          </contact:postal>
          <contact:email>john.doe@denic.de</contact:email>
          <contact:phone>+49.6927235x290</contact:phone>
          <contact:changed>2024-10-04T13:22:04+02:00</contact:changed>
        </domain:contact>
        <domain:contact role="holder">
          <contact:type>PERSON</contact:type>
        </domain:contact>
        <dnsentry:dnsentry xsi:type="dnsentry:A">
          <dnsentry:owner>domain-example-1000022.de.</dnsentry:owner>
          <dnsentry:rdata>
            <dnsentry:address>127.0.0.1</dnsentry:address>
          </dnsentry:rdata>
        </dnsentry:dnsentry>
        <domain:registrationDate>2024-10-04T13:31:25+02:00</domain:registrationDate>
        <domain:changed>2024-10-04T18:23:08+02:00</domain:changed>
        <domain:regAcc>
          <domain:regAccId>DENIC-1000022</domain:regAccId>
          <domain:name>DENIC eG</domain:name>
          <domain:email>1000022@opsblau.de</domain:email>
          <domain:phone>+49 69 27235 272</domain:phone>
          <domain:changed>2023-09-11T14:15:39+02:00</domain:changed>
        </domain:regAcc>
      </domain:infoData>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML response 5

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>9ca20332-cc31-436e-9f05-6160cd81845a</tr:stid>
    <tr:result>success</tr:result>
    <tr:message level="info" code="13000000011">
      <tr:text>Request was processed in test environment - not valid in real world</tr:text>
      <tr:argument>testing platform</tr:argument>
    </tr:message>
    <tr:data>
      <domain:infoData xmlns:domain="http://registry.denic.de/domain/5.0" xmlns:contact="http://registry.denic.de/contact/5.0" xmlns:dnsentry="http://registry.denic.de/dnsentry/5.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <domain:handle>domain-example-1000022.de</domain:handle>
        <domain:ace>domain-example-1000022.de</domain:ace>
        <domain:status>pendingCreate</domain:status>
        <domain:contact role="generalrequest">
          <contact:handle>DENIC-1000022-EXAMPLE-GR</contact:handle>
          <contact:type>REQUEST</contact:type>
          <contact:uri-template>mailto:://noreply@denic.de</contact:uri-template>
          <contact:changed>2024-10-04T13:21:16+02:00</contact:changed>
        </domain:contact>
        <domain:contact role="abusecontact">
          <contact:handle>DENIC-1000022-EXAMPLE-ABUSE</contact:handle>
          <contact:type>REQUEST</contact:type>
          <contact:uri-template>mailto:://noreply@denic.de</contact:uri-template>
          <contact:changed>2024-10-04T13:21:25+02:00</contact:changed>
        </domain:contact>
        <domain:contact role="holder">
          <contact:handle>DENIC-1000022-EXAMPLE-ORG</contact:handle>
          <contact:type>ORG</contact:type>
          <contact:name>DENIC eG</contact:name>
          <contact:postal>
            <contact:address>Theodor-Stern-Kai 1</contact:address>
            <contact:postalCode>60596</contact:postalCode>
            <contact:city>Frankfurt</contact:city>
            <contact:countryCode>DE</contact:countryCode>
          </contact:postal>
          <contact:email>john.doe@denic.de</contact:email>
          <contact:phone>+49.6927235x290</contact:phone>
          <contact:changed>2024-10-04T13:22:04+02:00</contact:changed>
          <verification:verificationInformation xmlns:verification="http://registry.denic.de/verification/5.0" xsi:type="verification:domainVerificationInformationType">
            <verification:verifiedClaims>
              <verification:claim>address</verification:claim>
              <verification:claim>name</verification:claim>
            </verification:verifiedClaims>
            <verification:verificationResult>success</verification:verificationResult>
            <verification:verificationReference>ABC123/45GHT</verification:verificationReference>
            <verification:verificationTimestamp>2023-11-11T10:11:00+01:00</verification:verificationTimestamp>
            <verification:verificationEvidence>company_register</verification:verificationEvidence>
            <verification:verificationMethod>electronic_document</verification:verificationMethod>
            <verification:trustFramework>de_denic</verification:trustFramework>
          </verification:verificationInformation>
        </domain:contact>
        <domain:contact role="holder">
          <contact:handle>DENIC-1000022-EXAMPLE-PERSON</contact:handle>
          <contact:type>PERSON</contact:type>
          <contact:name>John Doe</contact:name>
          <contact:postal>
            <contact:address>Theodor-Stern-Kai 1</contact:address>
            <contact:postalCode>60596</contact:postalCode>
            <contact:city>Frankfurt</contact:city>
            <contact:countryCode>DE</contact:countryCode>
          </contact:postal>
          <contact:email>john.doe@denic.de</contact:email>
          <contact:phone>+49.69272350</contact:phone>
          <contact:changed>2024-10-04T19:01:40+02:00</contact:changed>
          <verification:verificationInformation xmlns:verification="http://registry.denic.de/verification/5.0" xsi:type="verification:domainVerificationInformationType">
            <verification:verifiedClaims>
              <verification:claim>address</verification:claim>
            </verification:verifiedClaims>
            <verification:verificationResult>success</verification:verificationResult>
            <verification:verificationReference>ABC123/45GHA</verification:verificationReference>
            <verification:verificationTimestamp>2023-11-11T10:11:00+01:00</verification:verificationTimestamp>
            <verification:verificationEvidence>idcard</verification:verificationEvidence>
            <verification:verificationMethod>auth</verification:verificationMethod>
            <verification:trustFramework>de_denic</verification:trustFramework>
          </verification:verificationInformation>
          <verification:verificationInformation xmlns:verification="http://registry.denic.de/verification/5.0" xsi:type="verification:domainVerificationInformationType">
            <verification:verifiedClaims>
              <verification:claim>name</verification:claim>
            </verification:verifiedClaims>
            <verification:verificationResult>success</verification:verificationResult>
            <verification:verificationReference>ABC123/45GHN</verification:verificationReference>
            <verification:verificationTimestamp>2023-11-11T10:11:00+01:00</verification:verificationTimestamp>
            <verification:verificationEvidence>idcard</verification:verificationEvidence>
            <verification:verificationMethod>auth</verification:verificationMethod>
            <verification:trustFramework>de_denic</verification:trustFramework>
          </verification:verificationInformation>
        </domain:contact>
        <dnsentry:dnsentry xsi:type="dnsentry:A">
          <dnsentry:owner>domain-example-1000022.de.</dnsentry:owner>
          <dnsentry:rdata>
            <dnsentry:address>127.0.0.1</dnsentry:address>
          </dnsentry:rdata>
        </dnsentry:dnsentry>
        <domain:registrationDate>2024-10-04T13:31:25+02:00</domain:registrationDate>
        <domain:changed>2024-10-04T18:23:08+02:00</domain:changed>
        <domain:regAcc>
          <domain:regAccId>DENIC-1000022</domain:regAccId>
          <domain:name>DENIC eG</domain:name>
          <domain:email>1000022@opsblau.de</domain:email>
          <domain:phone>+49 69 27235 272</domain:phone>
          <domain:changed>2023-09-11T14:15:39+02:00</domain:changed>
        </domain:regAcc>
      </domain:infoData>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### XML request 4

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:domain="http://registry.denic.de/domain/5.0">
   <domain:info recursive="true">
      <domain:handle>domain-example-1000022.de</domain:handle>
      <domain:authInfo>My-Very-Secret-Auth-Info</domain:authInfo>
   </domain:info>
</registry-request>
```

### XML response 6

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>90ffa070-cd13-4f19-8868-d8a29a32fa84</tr:stid>
    <tr:result>success</tr:result>
    <tr:message level="info" code="13000000011">
      <tr:text>Request was processed in test environment - not valid in real world</tr:text>
      <tr:argument>testing platform</tr:argument>
    </tr:message>
    <tr:data>
      <domain:infoData xmlns:domain="http://registry.denic.de/domain/5.0" xmlns:contact="http://registry.denic.de/contact/5.0" xmlns:dnsentry="http://registry.denic.de/dnsentry/5.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <domain:handle>domain-example-1000022.de</domain:handle>
        <domain:ace>domain-example-1000022.de</domain:ace>
        <domain:status>pendingCreate</domain:status>
        <domain:authInfo>true</domain:authInfo>
        <domain:contact role="generalrequest">
          <contact:type>REQUEST</contact:type>
          <contact:uri-template>mailto:://noreply@denic.de</contact:uri-template>
          <contact:changed>2024-10-04T13:21:16+02:00</contact:changed>
        </domain:contact>
        <domain:contact role="abusecontact">
          <contact:type>REQUEST</contact:type>
          <contact:uri-template>mailto:://noreply@denic.de</contact:uri-template>
          <contact:changed>2024-10-04T13:21:25+02:00</contact:changed>
        </domain:contact>
        <domain:contact role="holder">
          <contact:type>ORG</contact:type>
          <contact:name>DENIC eG</contact:name>
          <contact:postal>
            <contact:address>Theodor-Stern-Kai 1</contact:address>
            <contact:postalCode>60596</contact:postalCode>
            <contact:city>Frankfurt</contact:city>
            <contact:countryCode>DE</contact:countryCode>
          </contact:postal>
          <contact:email>john.doe@denic.de</contact:email>
          <contact:phone>+49.6927235x290</contact:phone>
          <contact:changed>2024-10-04T13:22:04+02:00</contact:changed>
          <verification:verificationInformation xmlns:verification="http://registry.denic.de/verification/5.0" xsi:type="verification:domainVerificationInformationType">
            <verification:verifiedClaims>
              <verification:claim>address</verification:claim>
              <verification:claim>name</verification:claim>
            </verification:verifiedClaims>
            <verification:verificationResult>success</verification:verificationResult>
          </verification:verificationInformation>
        </domain:contact>
        <domain:contact role="holder">
          <contact:type>PERSON</contact:type>
          <contact:name>John Doe</contact:name>
          <contact:postal>
            <contact:address>Theodor-Stern-Kai 1</contact:address>
            <contact:postalCode>60596</contact:postalCode>
            <contact:city>Frankfurt</contact:city>
            <contact:countryCode>DE</contact:countryCode>
          </contact:postal>
          <contact:email>john.doe@denic.de</contact:email>
          <contact:phone>+49.69272350</contact:phone>
          <contact:changed>2024-10-04T19:01:40+02:00</contact:changed>
          <verification:verificationInformation xmlns:verification="http://registry.denic.de/verification/5.0" xsi:type="verification:domainVerificationInformationType">
            <verification:verifiedClaims>
              <verification:claim>address</verification:claim>
            </verification:verifiedClaims>
            <verification:verificationResult>success</verification:verificationResult>
          </verification:verificationInformation>
          <verification:verificationInformation xmlns:verification="http://registry.denic.de/verification/5.0" xsi:type="verification:domainVerificationInformationType">
            <verification:verifiedClaims>
              <verification:claim>name</verification:claim>
            </verification:verifiedClaims>
            <verification:verificationResult>success</verification:verificationResult>
          </verification:verificationInformation>
        </domain:contact>
        <dnsentry:dnsentry xsi:type="dnsentry:A">
          <dnsentry:owner>domain-example-1000022.de.</dnsentry:owner>
          <dnsentry:rdata>
            <dnsentry:address>127.0.0.1</dnsentry:address>
          </dnsentry:rdata>
        </dnsentry:dnsentry>
        <domain:registrationDate>2024-10-04T13:31:25+02:00</domain:registrationDate>
        <domain:changed>2024-10-04T18:23:08+02:00</domain:changed>
        <domain:regAcc>
          <domain:regAccId>DENIC-1000022</domain:regAccId>
          <domain:name>DENIC eG</domain:name>
          <domain:email>1000022@opsblau.de</domain:email>
          <domain:phone>+49 69 27235 272</domain:phone>
          <domain:changed>2023-09-11T14:15:39+02:00</domain:changed>
        </domain:regAcc>
      </domain:infoData>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### Key/Value format request (alternative wire format)

```
Version: 5.0
Action: INFO
Domain: domain-example-1000022.de
Recursive: false
```

### Key/Value format response

```
RESULT: success
STID: 534b0ec4-83fa-4255-9601-b110e47616be

Domain: de-example.de
Domain-Ace: de-example.de
Nsentry: de-example.de. IN A 81.91.170.12
Status: connect
RegistrationDate: 2024-10-04T13:31:25+02:00
Changed: 2024-10-04T18:23:08+02:00

[General Request]

[Abuse Contact]

[Holder]

[Holder]

[RegAcc]
RegAccId: DENIC-1000022
Name: DENIC eG
```

### Key/Value format response 2

```
RESULT: success
STID: c7c97267-5d28-4362-ba95-9b4ae3109ab7

Domain: de-example.de
Domain-Ace: de-example.de
Nsentry: de-example.de. IN A 81.91.170.12
Status: connect
RegistrationDate: 1992-01-01T08:46:32+02:00
VerificationDeadlineBeforeDedelegation: 2024-06-05T00:00:00+02:00
VerificationDeadlineBeforeDeletion: 2024-09-05T00:00:00+02:00
Changed: 2019-04-05T09:55:37+02:00

[General Request]
Handle: DENIC-1000022-DENIC-GR

[Abuse Contact]
Handle: DENIC-1000022-DENIC-ABUSE

[Holder]
Handle: DENIC-1000022-DENIC-ORG

[Holder]
Handle: DENIC-1000022-DENIC-PERSON

[RegAcc]
RegAccId: DENIC-1000022
Name: DENIC eG
```

### Key/Value format request (alternative wire format) 2

```
Version: 5.0
Action: INFO
Domain: domain-example-1000022.de
Authinfo: My-Very-Secret-Auth-Info
Recursive: false
```

### Key/Value format response 3

```
RESULT: success
STID: 0c71c5a3-70eb-4194-b6de-4282ff414b44

Domain: de-example.de​
Domain-Ace: de-example.de​
Nsentry: de-example.de. IN A 81.91.170.12​
Status: connect​
RegistrationDate: 1992-01-01T08:46:32+02:00​
​VerificationDeadlineBeforeDedelegation: 2024-06-05T00:00:00+02:00
VerificationDeadlineBeforeDeletion: 2024-09-05T00:00:00+02:00
Changed: 2019-04-05T09:55:37+02:00​

[General Request]

[Abuse Contact]

[Holder]

[RegAcc]
RegAccId: DENIC-1000022
Name: DENIC eG
```

### Key/Value format request (alternative wire format) 3

```
Version: 5.0
Action: INFO
Domain: domain-example-1000022.de
```

### Key/Value format response 4

```
RESULT: success
STID: 6c4a38f9-07d2-42d1-8fb0-8124e66ac6ed

Domain: de-example.de​
Domain-Ace: de-example.de​
Nsentry: de-example.de. IN A 81.91.170.12​
Status: connect​
RegistrationDate: 1992-01-01T08:46:32+02:00​
​VerificationDeadlineBeforeDedelegation: 2024-06-05T00:00:00+02:00
VerificationDeadlineBeforeDeletion: 2024-09-05T00:00:00+02:00
Changed: 2019-04-05T09:55:37+02:00​

[General Request]
Type: REQUEST​
URI-Template: mailto:dbs@denic.de​
​Changed: 2018-08-27T15:14:15+02:00​

[Abuse Contact]
Type: REQUEST​
URI-Template: mailto:abuse@denic.de​
Changed: 2018-08-27T15:14:15+02:00​ ​

[Holder]
Type: ORG
Name: DENIC eG
Address: Theodor-Stern-Kai 1
City: Frankfurt
PostalCode: 60596
CountryCode: DE
Email: john.doe@denic.de
Phone: +49.6927235x290
Changed: 2024-10-04T13:22:04+02:00

[VerificationInformation]​
VerifiedClaim: name​
VerificationResult: success​

[Holder]
Type: PERSON
Name: Max Mustermann
Address: Musterstraße 1
City: Musterstadt
PostalCode: 99999
CountryCode: DE
Email: max@mustermann.de
Phone: +49.1731234567
Changed: 2018-08-27T15:14:15+02:00​

[VerificationInformation]​
VerifiedClaim: address​
VerifiedClaim: name
VerificationResult: success​

[VerificationInformation]​
VerifiedClaim: email
VerificationResult: failed

[RegAcc]​
RegAccId: DENIC-22123​
Name: DENIC Services GmbH &amp; Co. KG​
Email: info@denic-services.de​
Phone: +49.61516290940​
Changed: 2018-08-27T15:14:15+02:00​
```

### Key/Value format response 5

```
RESULT: success
STID: 99849ee7-503b-46b4-868d-5ab3efa33a3c

Domain: de-example.de
Domain-Ace: de-example.de
Nsentry: de-example.de. IN A 81.91.170.12
Status: connect
RegistrationDate: 1992-01-01T08:46:32+02:00
VerificationDeadlineBeforeDedelegation: 2024-06-05T00:00:00+02:00
VerificationDeadlineBeforeDeletion: 2024-09-05T00:00:00+02:00
Changed: 2019-04-05T09:55:37+02:00

[General Request]​
Handle: DENIC-1000002-DENIC-GR
Type: REQUEST​
URI-Template: mailto:dbs@denic.de​
Changed: 2018-08-27T15:14:15+02:00​

[Abuse Contact]​
Handle: DENIC-1000002-DENIC-ABUSE
Type: REQUEST​
URI-Template: mailto:abuse@denic.de​
Changed: 2018-08-27T15:14:15+02:00​

[Holder]
Handle: DENIC-1000002-DENIC-ORG
Type: ORG
Name: DENIC eG
Address: Theodor-Stern-Kai 1-3
City: Frankfurt am Main
PostalCode: 60596
CountryCode: DE
Email: info@denic.de
Phone: +49.6927235x290
Changed: 2018-08-27T15:14:15+02:00​

[VerificationInformation]
VerifiedClaim: name
VerificationResult: success
VerificationReference: ABC123/45GHT1
VerificationTimestamp: 2023-11-11T15:36:21+02:00
VerificationEvidence: company_register
VerificationMethod: electronic_document
TrustFramework: de_denic

[Holder]
Handle: DENIC-1000002-PERSON
Type: PERSON
Name: Max Mustermann
Address: Musterstraße 1
City: Musterstadt
PostalCode: 99999
CountryCode: DE
Email: max@mustermann.de
Phone: +49.1731234567
Changed: 2018-08-27T15:14:15+02:00​

[VerificationInformation]
VerifiedClaim: address
VerifiedClaim: name
VerificationResult: success
VerificationReference: ABC123/45GHT2
VerificationTimestamp: 2023-11-11T15:36:21+02:00
VerificationEvidence: idcard
VerificationMethod: vdig
TrustFramework: de_denic

[VerificationInformation]
VerifiedClaim: email
VerificationResult: failed
VerificationReference: ABC123/45GHT3
VerificationTimestamp: 2023-11-11T15:36:21+02:00
VerificationEvidence: email_ver_transaction_log
VerificationMethod: reachability
TrustFramework: de_denic

[RegAcc]
RegAccId: DENIC-22123
Name: DENIC Services GmbH &amp; Co. KG
Email: info@denic-services.de
Phone: +49.61516290940
Changed: 2018-08-27T15:14:15+02:00​
```

### Key/Value format request (alternative wire format) 4

```
Version: 5.0
Action: INFO
Domain: domain-example-1000022.de
Authinfo: My-Very-Secret-Auth-Info
```

### Key/Value format response 6

```
Result: success
STID: 0a38e709-33e3-d5cf-cccf-622f9a16f225

Domain: de-example.de​
Domain-Ace: de-example.de​
Nsentry: de-example.de. IN A 81.91.170.12​
Status: connect​
RegistrationDate: 1992-01-01T08:46:32+02:00​
​VerificationDeadlineBeforeDedelegation: 2024-06-05T00:00:00+02:00
VerificationDeadlineBeforeDeletion: 2024-09-05T00:00:00+02:00
Changed: 2019-04-05T09:55:37+02:00​

[General Request]
Type: REQUEST
URI-Template: mailto:dbs@denic.de​
Changed: 2024-10-04T13:21:25+02:00

[Abuse Contact]
Type: REQUEST
URI-Template: mailto:abuse@denic.de
Changed: 2024-10-04T13:21:25+02:00

[Holder]
Type: ORG
Name: DENIC eG
Address: Theodor-Stern-Kai 1
City: Frankfurt
PostalCode: 60596
CountryCode: DE
Email: info@denic.de
Phone: +49.6927235x290
Changed: 2024-10-04T13:22:04+02:00

[VerificationInformation]
VerifiedClaim: address
VerifiedClaim: name
VerificationResult: success

[Holder]
Type: PERSON
Name: John Doe
Address: Theodor-Stern-Kai 1
City: Frankfurt
PostalCode: 60596
CountryCode: DE
Email: max@mustermann.de
Phone: +49.69272350x290
Changed: 2024-10-04T19:01:40+02:00

[VerificationInformation]
VerifiedClaim: address
VerificationResult: success

[VerificationInformation]
VerifiedClaim: name
VerificationResult: success

[VerificationInformation]
VerifiedClaim: email
VerificationResult: failed

[RegAcc]
RegAccId: DENIC-1000022
Name: DENIC eG
Email: info@denic.de
Phone: +49.6927235272
Changed: 2023-09-11T14:15:39+02:00
```
