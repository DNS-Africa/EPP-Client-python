# regaccINFO

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/regaccINFO.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/regaccINFO.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0" xmlns:regacc="http://registry.denic.de/regacc/5.0">
   <regacc:info>
      <regacc:handle>DENIC-99995</regacc:handle>
   </regacc:info>
</registry-request>
```

### XML response

```xml
<?xml version="1.0" encoding="UTF-8"?>

<registry-response xmlns="http://registry.denic.de/global/5.0" xmlns:tr="http://registry.denic.de/transaction/5.0">
  <tr:transaction>
    <tr:stid>eb7c2a09-a963-11e9-aba1-217bf86bcda0</tr:stid>
    <tr:result>success</tr:result>
    <tr:data>
      <regacc:infoData xmlns:regacc="http://registry.denic.de/regacc/5.0">
        <regacc:handle>DENIC-99995</regacc:handle>
        <regacc:name>DENIC eG - Business Services</regacc:name>
        <regacc:postal>
          <regacc:address>DENIC eG</regacc:address>
          <regacc:address>Kaiserstraße 75-77</regacc:address>
          <regacc:postalCode>60329</regacc:postalCode>
          <regacc:city>Frankfurt</regacc:city>
          <regacc:countryCode>DE</regacc:countryCode>
        </regacc:postal>
        <regacc:phone>+49 69 27235 0</regacc:phone>
        <regacc:fax>+49 69 27235 235</regacc:fax>
        <regacc:email>dbs@denic.de</regacc:email>
        <regacc:url>http://www.denic.de</regacc:url>
        <regacc:memberacc>DENIC-99995</regacc:memberacc>
        <regacc:contact role="generalrequest">
          <contact:type xmlns:contact="http://registry.denic.de/contact/5.0">REQUEST</contact:type>
          <contact:uri-template xmlns:contact="http://registry.denic.de/contact/5.0">mailto:general@denic.de?subject=domain:{Ulabel}</contact:uri-template>
          <contact:changed xmlns:contact="http://registry.denic.de/contact/5.0">2019-01-01T01:00:00+01:00</contact:changed>
        </regacc:contact>
        <regacc:contact role="abusecontact">
          <contact:type xmlns:contact="http://registry.denic.de/contact/5.0">REQUEST</contact:type>
          <contact:uri-template xmlns:contact="http://registry.denic.de/contact/5.0">mailto:abuse@denic.de?subject=domain:{Ulabel}</contact:uri-template>
          <contact:changed xmlns:contact="http://registry.denic.de/contact/5.0">2019-01-01T01:00:00+01:00</contact:changed>
        </regacc:contact>
        <regacc:changed>2019-05-17T10:48:29+02:00</regacc:changed>
      </regacc:infoData>
    </tr:data>
  </tr:transaction>
</registry-response>
```

### Key/Value format request (alternative wire format)

```
Version: 5.0
Action: info
Regacc: DENIC-99995
```

### Key/Value format response

```
Result: success
STID: c69ae650-a962-11e9-aba1-217bf86bcda0
Regaccid: DENIC-99995
Name: DENIC eG - Business Services
Address: DENIC eG
Address: Theodor-Stern-Kai 1
Postalcode: 60596
City: Frankfurt am Main
Countrycode: DE
Phone: +49 69 27235 0
Fax: +49 69 27235 238
Email: dbs@denic.de
Url: http://www.denic.de
Memberaccid: DENIC-99995
Changed: 2019-05-17T10:48:29+02:00

[General Request]
Type: request
Uri-template: mailto:general@denic.de?subject=domain:{Ulabel}
Changed: 2019-01-01T01:00:00+01:00

[Abuse Contact]
Type: request
Uri-template: mailto:abuse@denic.de?subject=domain:{Ulabel}
Changed: 2019-01-01T01:00:00+01:00
```
