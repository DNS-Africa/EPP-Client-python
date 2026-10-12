# DENIC Message Codes (Error Codes)

DENIC reports every problem and notice as an 11-digit **message code** in the
`<tr:message code="...">` element (XML) or an `ERROR:`/`WARNING:`/`INFO:` line
(K/V). DENIC explicitly warns: **do not parse the human-readable text — branch
only on the numeric code**, because the text (including dynamic parts in
`[...]`) can change.

Source: [List of Message Codes](https://docs.denic.de/en/Content/DENIC-29/Liste-mit-Meldungscodes.htm) and
[Structure of Message Codes](https://docs.denic.de/en/Content/DENIC-29/Aufbau%20und%20Bestandteile%20einer%20Meldungskodierung.htm).

## Code structure

An 11-digit code `A B C D D D ...`:

| Position | Meaning |
|----------|---------|
| Digit 1 (A) | Classification |
| Digits 2–3 (B) | Interface |
| Digits 4–6 (C) | Module |
| Digits 7–11 (D…) | Sequence number |

**Digit 1 — Classification**

| Value | Meaning |
|-------|---------|
| 1 | INFO, success |
| 2 | INFO, failed |
| 3 | WARNING, temporary error |
| 4 | WARNING, permanent error |
| 5 | ERROR, temporary error |
| 6 | ERROR, permanent error |
| 7 | TECHNICALERROR, temporary error |
| 8 | TECHNICALERROR, permanent error |

**Digits 2–3 — Interface**

| Value | Meaning |
|-------|---------|
| 01, 02 | currently not used |
| 03 | RRI (.de) |
| 04 | RRI (.9.4.e164.arpa) |
| 05 | whois |
| 06 | not dependent on a particular interface |
| 09 | web application |

**Digits 4–6 — Module**

| Value | Meaning |
|-------|---------|
| 000 | Not dependent on a particular application |
| 100 | LOGIN / LOGOUT |
| 200 | Contact — not dependent on a particular module |
| 210 | CREATE (contact) |
| 220 | UPDATE (contact) |
| 300 | Domain — not dependent on a particular module |
| 310 | CREATE (domain) |
| 320 | UPDATE (domain) |
| 330 | CHHOLDER |
| 340 | RENEW (ENUM domain) |
| 345 | Expire (ENUM domain) |
| 348 | Expire (DE domain) |
| 350 | DELETE |
| 360 | TRANSIT |
| 370 | CHPROV |
| 391 | CREATE-AUTHINFO1 |
| 392 | DELETE-AUTHINFO1 |
| 393 | CREATE-AUTHINFO2 |
| 394 | AuthInfo-expire |
| 400 | CHECK |
| 450 | INFO |
| 500 | RAI — not dependent on a particular module |
| 600 | QUEUE — not dependent on a particular module |
| 610 | QUEUE-READ |
| 650 | QUEUE-DELETE |

## Full message-code table

| Code | Text |
|------|------|
| 11300088725 | AuthInfo deleted |
| 11300088726 | AuthInfo letter could not be delivered |
| 13000000011 | Request was processed in test environment – not valid in real world |
| 13000000022 | Used quota |
| 13350000001 | Domain bears a DISPUTE entry and can therefore not be restored |
| 16000063119 | DNS data was checked and accepted |
| 16330088732 | An action determines the removal of the AuthInfo |
| 16350000031 | Domain has been deleted [request-reference DENIC#:<Ticket-ID>] |
| 33000000022 | Used quota |
| 33300102900 | The provided DNS data are not acceptable. Domain "Status" is "failed". |
| 33300102912 | Predelegation Check warning |
| 46000108827 | Secure Entry Point flag should be set in DNSKEY |
| 53000000008 | Daily quota exceeded |
| 53000000012 | Concurrent write access to the same business object is prohibited [dynamic error text] |
| 53000020002 | Unauthorized request |
| 53000020013 | Verification of signature failed |
| 53000020019 | Signature of request is correct but too old |
| 53000060009 | At least one Contact does not exist |
| 53000080002 | This value cannot be deleted |
| 53000080011 | The request cannot be carried out because of an active DISPUTE |
| 53000080012 | Domain "Status" is "failed" |
| 53300062003 | The value for keyword "Domain" has an invalid format [dynamic error text] |
| 53300081600 | Within a Contact "Email" is missing |
| 53300100021 | Technical Predelegation Check Problem – please try later |
| 53300102902 | Required glue record is missing [dynamic error text] |
| 53300102912 | Nameserver error [dynamic error text] |
| 53300102920 | Occurrences of keyword "Nserver" out of range [min: 2, max: 13] |
| 53300103022 | Missing mail exchange preference of DNS entry |
| 53370080005 | Required change provider request data is missing |
| 53380062206 | Mismatch between values for "Domain-ace" and "Domain" |
| 56000000002 | Text part has not been encoded properly |
| 56000000027 | Mailheader is incomplete |
| 56000088709 | Specified AuthInfo2 does not exist |
| 56300108812 | The provided DNS data are not acceptable |
| 56310082011 | Domain "Status" is "redemptionPeriod" |
| 58000000002 | Text part has not been encoded properly |
| 58000000027 | Mailheader is incomplete |
| 63000000006 | The request has an invalid key/value pair format |
| 63000000007 | Request shows semantics error [dynamic error text] |
| 63000000012 | Unknown Error |
| 63000040110 | Keyword "Action" cannot be recognized |
| 63000040410 | Keyword "Version" cannot be recognized |
| 63000060003 | An indicated Contact is invalid [repetition of the invalid handle] |
| 63000060008 | The value contains one or more invalid characters [dynamic error text] |
| 63000060015 | The value is too long [dynamic error text] |
| 63000060102 | Inadmissible value for keyword "Action" |
| 63000060402 | Inadmissible value for keyword "Version" |
| 63000060504 | "CTID" has been used before [dynamic error text] |
| 63000060508 | Inadmissible value for keyword "Ctid" |
| 63000080009 | Request type is missing, either keyword "Domain" or "Handle" |
| 63100020005 | Number of failed logins exceeds allowed maximum |
| 63100040202 | Keyword "User" must appear once and just once |
| 63100040302 | Keyword "Password" must appear once and just once |
| 63100064002 | Authorization failure |
| 63200020603 | This Contact is administered by another provider [dynamic error text] |
| 63200040602 | Keyword "Handle" or "Domain" must appear once and just once |
| 63200040610 | Keyword "Handle" cannot be recognized |
| 63200040702 | Keyword "Type" must appear once and just once |
| 63200040710 | Keyword "Type" cannot be recognized |
| 63200040802 | Keyword "Name" must appear once and just once |
| 63200040810 | Keyword "Name" cannot be recognized |
| 63200041010 | Keyword "Address" cannot be recognized |
| 63200041102 | Keyword "PostalCode" must appear once and just once |
| 63200041110 | Keyword "PostalCode" cannot be recognized |
| 63200041202 | Keyword "City" must appear once and just once |
| 63200041210 | Keyword "City" cannot be recognized |
| 63200041302 | Keyword "CountryCode" must appear once and just once |
| 63200041310 | Keyword "CountryCode" cannot be recognized |
| 63200041610 | Keyword "Email" cannot be recognized |
| 63200041802 | Keyword "Disclose" can appear once and just once |
| 63200060702 | Inadmissible value for keyword "Type" |
| 63200061302 | The value for "CountryCode" is not a valid ISO code |
| 63200061603 | The value for keyword "Email" has an invalid format |
| 63200061708 | Invalid character(s) in "Sip" value |
| 63200061802 | Inadmissible value for keyword "Disclose" |
| 63200080108 | This value of "Action" is not permitted here |
| 63200080900 | Keyword "Organisation" invalid with "Type" "ORG" |
| 63220080701 | The value of "Type" cannot be changed with an UPDATE |
| 63220080801 | The value of "Name" cannot be changed with an UPDATE |
| 63300022003 | This domain is administered by another provider [dynamic error text] |
| 63300042100 | Keyword "Domain-ace" cannot be recognized |
| 63300042102 | Keyword "Domain-ace" can appear once and just once |
| 63300043003 | Occurences of keyword "Nsentry" out of range [dynamic error text] |
| 63300043100 | Keyword "Nserver" or "Nsentry" cannot be recognized |
| 63300060005 | Contact occurs more than once in same role |
| 63310062008 | Inadmissible value for keyword "RegAcc" [Repeat of the user entry] |
| 63300062009 | Domain doesn't exist [repetition of the non-existent domain] |
| 63300062010 | RegAcc doesn't exist [Repeat of the RegAcc] |
| 63300062905 | Duplicate value(s) for "Nserver" |
| 63300063002 | Preference values for MX-RR are out of range (0-999) |
| 63300063003 | Incorrect value(s) for "Nsentry" |
| 63300063005 | Duplicate value for "Nsentry" record is present |
| 63300063006 | "Nsentry" has invalid owner |
| 63300063011 | Nserver has invalid owner [dynamic error text] |
| 63300063016 | At least 2 MX entries have the identical preference |
| 63300063102 | Unknown type of DNS data |
| 63300063103 | Illegal type of DNS data |
| 63300080010 | Required domain data is missing |
| 63300080013 | Too many Contacts are indicated |
| 63300080700 | Contact with wrong value for "Type" |
| 63300083005 | Value for "Nsentry" contains unknown host |
| 63300102913 | Incorrect value(s) for "Nserver" [dynamic error text] |
| 63300103005 | No other MX resource record is allowed in combination with "Null MX" |
| 63310062004 | Domain already exists |
| 63310062007 | Inadmissible value for keyword "Domain" [dynamic error text] |
| 63360043403 | Keyword "Disconnect" can appear once and just once |
| 63360063402 | Inadmissible value for keyword "Disconnect" |
| 63360082531 | For TRANSIT, a Holder Handle is mandatory |
| 63370048700 | Keyword "AuthInfo" cannot be recognized [dynamic error text] |
| 63370088701 | AuthInfo does not match [dynamic error text] |
| 63380063209 | Illegal operation on own domain |
| 63391048502 | Keyword "AuthInfoHash" must appear once and just once |
| 63391048602 | Keyword "AuthInfoExpire" can appear once and just once |
| 63391068503 | The value for keyword "AuthInfoHash" has an invalid format |
| 63391068603 | The value for keyword "AuthInfoExpire" has an invalid format |
| 63391068704 | AuthInfo1 already exists |
| 63391082031 | Domain has Description |
| 63392068709 | AuthInfo1 does not exist |
| 63393068704 | AuthInfo2 already exists |
| 63450043902 | Keyword "Recursive" can appear once and just once |
| 63450063902 | Inadmissible value for keyword "Recursive" |
| 63600063502 | Inadmissible value for keyword "MsgType" |
| 63650063607 | This message is not the oldest |
| 63650063609 | MsgId does not exist |
| 63900042502 | Keyword "Holder" must appear once and just once |
| 66000020020 | Invalid Signature Algorithm |
| 66300048905 | Invalid DNS Data (Nsentry, Dnskey) |
| 66300063003 | Missing mail exchange host |
| 66300063006 | "Nsentry" has invalid owner |
| 66300063023 | AAAA resource record requires corresponding A resource record |
| 66300068803 | The value for keyword "Dnskey" has an invalid format |
| 66300068807 | "Dnskey" invalid |
| 66310082014 | Domain is not in Redemption Grace Period |
| 73100000005 | The maximum number of permitted login is reached |
| 76000000001 | Registry Service temporarily not available |
| 76000000002 | Timeout while processing request |
| 83000000000 | Request message too long [dynamic error text] |
| 83000000002 | The encoding specified is not supported |
| 83000000004 | Validation of XML request against Schema failed |
| 83000000005 | Validation of URI-Template failed [dynamic error text] |
| 83000000010 | Login failed |

> The `83000000005` URI-Template entry has several dynamic-text variants in the
> source (empty template, too long > 1024 chars, invalid scheme, invalid
> variable, invalid variable name).

## Additional codes found in command-specific / verification tables

| Code | Text | Where seen |
|------|------|-----------|
| 53000080014 | Domain "Status" is "pendingCreate" | domain CREATE (INFO) |
| 54300062506 | Holder does not match | domain CHPROV |
| 53380042010 | Keyword "Domain" cannot be recognized | domain commands |
| 63200042402 | Keyword "Phone" must appear once and just once | contact CREATE / UPDATE |
| 63200062603 | The value for keyword "Phone" has an invalid format | contact CREATE / UPDATE |
| 63300085940 | Missing phone for holder [dynamic error text] | domain CHHOLDER / CHPROV / RESTORE |
| 63650043610 | Keyword "MsgId" cannot be recognized | QUEUE-DELETE |

## Verification (KVK) message codes

Source: [List of Message Codes for Verification](https://docs.denic.de/en/Content/DENIC-29/Liste-mit-Meldungscodes-zur-Verifikation.htm)

| Code | Text |
|------|------|
| 63450064002 | One of the indicated values is not valid for this contact type [VerificationInformation] |
| 63200062603 | Incomplete verification information [missing keyword] |
| 63200041860 | Incomplete verification information [missing VerificationInformation] |
| 63200041861 | Inadmissible value in verification information [dynamic error text] |
| 63200041862 | Occurrences of verification information out of range |
| 63200041863 | Conflicting verification information [verificationReference 'value'] |
| 63200041865 | Duplicate value in verification information [keyword 'name', 'address' or 'email'] |
| 63200041866 | Duplicate key in verification information [keyword] |
| 63200041867 | Invalid combination of verification information |
