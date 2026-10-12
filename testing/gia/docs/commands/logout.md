# logout

> Source: [https://docs.denic.de/en/Content/Beispiele/50/Request/logout.htm](https://docs.denic.de/en/Content/Beispiele/50/Request/logout.htm)

### XML request

```xml
<!-- request -->

<?xml version="1.0" encoding="UTF-8" standalone="yes"?>

<registry-request xmlns="http://registry.denic.de/global/5.0">
 <logout/>
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
Action: logout
```

### Key/Value format response

```
Result: success
STID: 0b97f9b7-9f0b-11df-a9e2-9519b5688882
```
