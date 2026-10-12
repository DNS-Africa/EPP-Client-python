# login

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/login.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/login.htm)

### XML request

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0">
 <login>
  <user>DENIC-80121-USER1</user>
  <password>dsnfsd651</password>
 </login>
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
Action: login
User: user1
Password: password1
```

### Key/Value format response

```
Result: success
STID: 0b97f9b7-9f0b-11df-a9e2-9519b5688882
```
