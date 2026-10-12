# DENIC Data Model — Field Reference

Field-by-field reference for the DENIC RRI data objects. Each table maps the
key/value (K/V) keyword to the XML element, occurrence, type/length, value range
and policy. This is the primary reference for translating between DENIC and
EPP field semantics.

> Sources: DENIC-29 "Datenobjekt …" and "Datentypen und Wertebereiche" pages
> (see links at the bottom of each section).


## Domain data object

| K/V Keyword | XML Namespace and Element | Occurrencemin - max | Type / Length | Value Range | Description | Policy |
| Domain | domain:handle | 1 | token4 - 66 | domain-rule | This is the domain name. | - |
| Domain-Ace | domain:ace | 0 - 1 | token4 - 66 | domainace-rule | This is the ACE form (ASCII Compatible Encoding) of the domain name. | - |
| Holder | domain:contact role="holder" | 1 - 5 | token9 - 32 | contact-rule | This is the handle ID of the domain holder. | Only Contacts of the PERSON or ORG type are permitted.If several domain holders exist, all the handle IDs must be different. |
| GeneralRequest | domain:contact role="generalrequest" | 0-1 | token9 - 32 | contact-rule | Handle-Id of General Request | Only contacts of the REQUEST types are permitted |
| AbuseContact | domain:contact role="abusecontact" | 0-1 | token9 - 32 | contact-rule | Handle-Id of Abuse Contact | Only contacts of the REQUEST types are permitted. |
| Name server records |
| Nserver | dnsentry:owner | 2 - 13 | token1 - 254 | nserver-rule | If you use the k/v format: host name of name serverIf you use the XML format: ACE form of domain | The name servers must meet the requirements of the Predelegation Checks (see documentation "Nameserver Predelegation Check"). |
| - | dnsentry:nameserver | 0-13 | token1 - 254 | nserver-rule | This is the host name of the name server. | For name servers whose host name is located within the domain for which they make available the DNS, you must state an IPv4 address. Indication of an IPv6 address is optional. |
| - | dnsentry:address | 0-13 | token7-39 | ip-ruleIPv4 addresses according to RFC791 - INTERNET PROTOCOL DARPA INTERNET PROGRAM PROTOCOL SPECIFICATION in „dotted-quad“ format | This is the IPv4 address of the name server | You must state the IPv4 address. |
| - | dnsentry:addressV6 | 0-8 | token7-39 | ip-ruleIPv6 addresses according to RFC4291 IP Version 6 Addressing Architectureas „preferred form“. | This is the IPv6 address of the name server | You must state the IPv6 address. |
| Dnskey | dnsentry:flagsdnsentry:protocoldnsentry:algorithmdnsentry:publicKey | 0-20 | token30 - 999 | dnskey-ruleSyntax according to RFC4034 - Resource Records for the DNS Security Extensions, DNSKEY as „presentation format“ | Dnskey | The following four values must be stated:Flags: 256 or 257Protocol: at present always 3Numeric encoding of algorithm that is used:3 (DSA/SHA1)5 (RSA/SHA-1)6 (DSA-NSEC3-SHA1)7 (RSASHA1-NSEC3-SHA1)8 (RSA/SHA-256)10 (RSA/SHA-512)12 (GOST)13 (ECDSA-256)14 (ECDSA-512)Public key: base64-encodedYou will find descriptions of the DNSSEC-specific Predelegation Checks in the documentation "Nameserver Predelegation Check" |
| Alternative: Nsentries |
| IN A record: |
| Nsentry | dnsentry:owner | 1 - 5 | token4 - 252 | nsentry-rule | This is a domain which shall be registered or a sub-domain of the domain to be registered, including the ".de" | State in ACE form |
| dnsentry:address | token3 - 39 | ip-rule | This is the IPv4/IPv6 address of the hostConsecutive colons (::) as unspecified address are supported and resolved before starting the length check. | IPv4addresses according to RFC791 - INTERNET PROTOCOL DARPA INTERNET PROGRAM PROTOCOL SPECIFICATION in „dotted-quad“ formatIPv6addresses according to RFC4291 - IP Version 6 Addressing Architecture in „preferred form“ |
| IN MX-record: |
| Nsentry | dnsentry:owner | 1 - 5 | token4 - 252 | nsentry-rule | This is the domain or the sub-domain: You may enter a wildcard (*.domain.de) when MX-records are used.Length including the ".de" | State in ACE form |
| dnsentry:preference | unsignedShort | mxpref-rule | This is the MX preference value. | 0 = highest preference to 999 = lowest preference |
| dnsentry:exchange | token4 - 252 | mx-rule | This is the name of the relevant mail server.Length including the ".de" | State in ACE form. for a "Null MX" No Service Resource Record for Domains That Accept No Mail |
| Status | domain:status | 1 | enumeration | status-erule | This is the status of the domain. | Will be automatically assigned by the system. |
| Expire | domain:expire | 0 – 1 | dateTime25 | date-rule | This is the date, when a domain with the "failed" status is deleted. | Will be automatically assigned by the system. |

Source: <https://docs.denic.de/en/Content/DENIC-29/Datenobjekt%20Domain.htm>


## Contact data object (PERSON / ORG, and REQUEST)

| K/V Keyword | XML Namespace and Element | Occurrencemin - max | Type / Length | Value Range | Description | Policy |
| Handle | contact:handle | 1 | token9 - 32 | contact-rule | This is the unique ID of the Contact.Syntax: <RegAccId>-<MemberID > | A Contact handle must always start with the RegAccId of the administering RegAcc. |
| Type | contact:type | 1 | enumeration | role-erule | These Contact types are available:PERSON = natural person,ORG = a legal person (company, association, grouping of holders, organization etc., such as "DENIC eG") | The type of contact can be changed later. For Holder you may only use the types PERSON or ORG. |
| Name | contact:name | 1 | normalizedString1 - 255 | name-rule | This is the Contact's name. | Once set, you cannot change the keyword "name" any more. |
| Organisation | contact:organisation | 0 - * | normalizedString1 - 255 | organisation-rule | This is the organisation which is represented by the Contact. | You may only use the types PERSON. Cannot be changed, if the domain bears a DISPUTE entry. You must always state the domain holder in the "Name:" field. The "Organization" value has no right to the domain and is not entitled to apply for an AuthInfo or a provider change or similar. |
| Address | contact:address | 1 - * | normalizedString1 - 255 | address-rule | Street and house number of Contact | The keyword cannot be changed if the Contact is referenced as the holder of a domain which bears a DISPUTE entry. |
| PostalCode | contact:postalCode | 1 | token1 - 20 | postalcode-rule | Postal code and address of Contact | The keyword cannot be changed if the Contact is referenced as the holder of a domain which bears a DISPUTE entry. |
| City | contact:city | 1 | normalizedString1 - 80 | city-rule | Place of residence of Contact | The keyword cannot be changed if the Contact is referenced as the holder of a domain which bears a DISPUTE entry. |
| CountryCode | contact:countryCode | 1 | Enumeration2 | country-erule | Country code of the country in which the Contact's place of residence is located | You must use the country code of the ISO-3166-1 alpha-2 list ISO-3166-1 alpha-2 Liste. The keyword cannot be changed if the Contact is referenced as the holder of a domain which bears a DISPUTE entry. |
| Email | contact:email | 1 - * | normalizedString3 - 255 | email-rule(see RFC5322 - Internet Message Format) | E-mail address of Contact | „email” always is a mandatory field and must be specified at least once for the types PERSON and ORG in Contact CREATE and Contact UPDATE requests |

| K/V Keyword | XML Namespace and Element | Occurrencemin - max | Type / Length | Value Range | Description | Policy |
| Handle | contact:handle | 1 | token9 - 32 | contact-rule | This is the unique ID of the Contact.Syntax: <RegAccId>-<MemberID > | A Contact handle must always start with the RegAccId of the administering RegAcc. |
| Type | contact:type | 1 | enumeration | role-erule | REQUEST = an e-mail address or a URL in the URI-Template format. | For General Request and Abuse Contact you may only use the type REQUEST. |
| URI-Template | contact:uri-template | 1 | normalizedString8 - 1024 | Syntax as defined in RFC 6570 - URI Template | The variables Ulabel and Alabel in the URI-Template are replaced with the domain at a domain query (web-whois). | In case of a CREATE request, the content of the URI-Template is converted into a URL or e-mail as a test (For Alabel and Ulabel, a sample domain is used.) to check the syntax on correctness. |

Source: <https://docs.denic.de/en/Content/DENIC-29/Datenobjekt%20Contact.htm>


## Chprov data object (provider change)

| K/V Keyword | XML Namespace and Element | Occurrencemin - max | Type / Length | Value Range | Description | Policy |
| AuthInfo | authinfo | 1 | token1 - 255 | authinfo-rule | An AuthInfo1 or AuthInfo2 is stated. | The transferred AuthInfo must match an AuthInfo1 or AuthInfo2 stored in the DENIC database. |
| AuthInfoHash | hash | 1 | token64 | authinfohash-rule | This is the hash value of the stored AuthInfo1. | - |
| AuthInfoExpire | expire | 0 - 1 | token8 | digit-rule | This is the term of validity of the AuthInfo1. | The EXPIRE date can be 30 days ahead at maximum. The default is the current date + 30 calendar days. |

Source: <https://docs.denic.de/en/Content/DENIC-29/Datenobjekt%20Chprov.htm>


## Public registrar contact details (RegAcc) data object

| K/V Keyword | XML Namespace and Element | Occurrencemin - max | Type / Length | Value Range | Description | Policy |
| RegAccId | regacc:handle | 1 | token7 - 13 | regaccid-rule | The RegAccId is issued by DENIC and is composed of "DENIC-" and a numerical value. It is used to uniquely identify the RegAcc. | - |
| Name | regacc:name | 1 | normalizedString1 - 255 | Name-rule | This is the holder of the registration account. | Once set, you cannot change the keyword "name" any more. |
| Address | regacc:address | 1 - * | normalizedString1 - 255 | address-rule | Street and house number | - |
| PostalCode | regacc:postalCode | 0 - 1 | token9 - 32 | postalcode-rule | This is the postal code. | Some countries do not have postal code system; therefore "0" is a valid value. |
| City | regacc:city | 1 | normalizedString 1 - 80 | city-rule | This is the town or city. | - |
| CountryCode | regacc:countryCode | 1 | enumeration2 | country-erule | This is the applicable country code. | You must use the country code of the ISO-3166-1 alpha-2 List |
| Phone | regacc:phone | 1 - * | normalizedString1 - 255 | phone-rule | This is the phone number of the registrar.Please use the international format in accordance with the ITU-T E.123 standard (E.123 : Notation for national and international telephone numbers, e-mail addresses and web addresses)The first character must be a "+", and it must be followed by the country dialling code. | - |
| Fax | regacc:fax | 1 - * | normalizedString1 - 255 | phone-rule | This is the fax number of the registrar.We recommend to use the international format as defined by the ITU-T E.123 standard (E.123 : Notation for national and international telephone numbers, e-mail addresses and web addresses)The first character must be a "+", and it must be followed by the country dialling code. | - |
| Email | regacc:email | 1 | normalizedString3 - 255 | email-rulesee RFC5322 - Internet Message Format | This is the e-mail address of the registrar. | - |
| URL | regacc:url | 0 - 1 | normalizedString11 - 255 | Syntax as defined in RFC 3986 - Uniform Resource Identifier (URI): Generic Syntax | This is the URL of the registrar. | - |
| MemberAccId | regacc:memberacc | 1 | token7 - 13 | regaccid-rule | The MemberAccId is issued by DENIC and is composed of "DENIC-" and a numerical value. It is used to uniquely identify the MemberAcc. | - |
| Changed | regacc:changed | 1 | dateTime | date-rule | Date and time format according to ISO 8601 Date and time format | The same format is used for all services to specify the date and time in INFO and WHOIS outputs.The date and time specified for the RegAcc is updated as soon as the data for General Request and/or Abuse Contact have been changed. |
| Type | contact:type | 0 - 2 | enumeration7 | role-erule | Typ of the contact:REQUEST = E-mail address or URL | Once set, the Contact type cannot be changed any more. |
| URI-Template | contact:uri-template | 0 - 2 | normalizedString8 - 1024 | Syntax as defined in RFC 6570 URI Template | URI template with the optional variables "Alabel" and "Ulabel" that can be used for domainsIn case of a CREATE request, the content of the URI-Template is converted into a URL or e-mail as a test (For Alabel and Ulabel, a sample domain is used.) to check the syntax on correctness. | This is to be used in relation with General Request and Abuse Contact. Notice |  | It is mandatory to specify a General Request in the RegAcc profile. |

Source: <https://docs.denic.de/en/Content/DENIC-29/Datenobjekt%20%C3%B6ffentlicher%20Registrar-Kontaktdaten.htm>


## Data types and value ranges

| Data Types | Comment |
| normalizedString | A normalizedString represents white space normalized strings. The value range of normalizedString is the set of strings that do not contain the carriage return (%xD), line feed (%xA) or tab (%x9) characters. For detailed information about the data type go to normalizedString. |
| token | A token represents tokenized strings. The value range of token is the set of strings that do not contain the carriage return (%xD), line feed (%xA) or tab (%x9) characters, that have no leading or trailing spaces (%x20) and that have no internal sequences of two or more spaces. For detailed information about the data type token go to token . |
| enumeration | Enumeration constrains the value range to a specified set of values. For detailed information about enumeration go to enumeration . |
| date-time | The data type datetime is used to state a date and a time and a specific time zone. The syntax follows the rules stipulated in the standard ISO 8601:Dates are written: YYYY-MM-DD.Then follows T (for time) as a separator between date and time.Then follows the time, which is written: hh:mm:ss.Then follows recommended information, the difference to the coordinated universal time (UTC).It is written: +hh:mm Example: 2010-04-07T13:16:00+01:00 |
| unsignedShort | The data type unsignedShort designates an integer value in the value range 0 through 65535. For detailed information about the data type unsignedShort go to unsingedShort . |
| boolean | boolean may have either of two values - "true" and "false". For detailed information about the data type boolean go to boolean . |

| Type | Value Ranges | Definition |
| ace-val | %xx41-%x5A / %x61-%x7A / %x2D | A-Z / a-z / hyphen |
| alpha-val | %x41-%x5A / %x61-%x7A | A-Z / a-z |
| authinfo-val | %x41-%x48 %x4A-%x4E %x50-%x5A %x61-%x6B %x6D-%x6E %x70-%x7A / %x32-%x39 / %x2B / %x2D / %x2F / %x2A | A-H J-N P-Z a-k m-n p-z / 2-9 / plus sign / hyphen / slash / asterisk |
| digit-val | %x30-%x39 | 0-9 |
| dnskeyval | %x41-%x5A / %x61-%7A / %x30-39 / %x2D / %x2E / %x2F / %x2B | A-Z / a-z / 0-9 / hyphen / dot / slash / plus sign |
| idn-val | %xE1 / %xE0 / %x103 / %xE2 / %xE5 / %xE4 / %xE3 / %x105 / %x101 / %xE6 / %x107 / %x109 / %x10D / %x10B / %xE7 / %x10F / %x111 / %xE9 / %xE8 / %x115 / %xEA / %x11B / %xEB / %x117 / %x119 / %x113 / %x11F / %x11D / %x121 / %x123 / %x125 / %x127 / %xED / %xEC / %x12D / %xEE / %xEF / %x129 / %x12F / %x12B / %x131 / %x135 / %x137 / %x13A / %x13E / %x13C / %x142 / %x144 / %x148 / %xF1 / %x146 / %x14B / %xF3 / %xF2 / %x14F / %xF4 / %xF6 / %x151 / %xF5 / %xF8 / %x14D / %x153 / %x138 / %x155 / %x159 / %x157 / %x15B / %x15D / %x161 / %x15F / %x165 / %x163 / %x167 / %xFA / %xF9 / %x16D / %xFB / %x16F / %x171 / %x169 / %x173 / %x16B / %x175 / %xFD / %x177 / %xFF / %x17A /17E / %x17C / %xF0 / %xFE / %xDF | áàăâåäãąāæćĉčċçďđéèĕêěëėęēğĝġģĥħíìĭîïĩįīıĵķĺľļłńňñņŋóòŏôöőõøō oeĸŕřŗśŝšşťţŧúùŭûůüűũųūŵýŷÿźžżðþß |
| ip-val | %x30-%x39 / %x2E / %x3A | ASCII: 0-9 / dot / colon |
| name-val | %x41-%x5A / %x61-%x7A / %x30-%x39 / %x20 / %x26 / %x2D / %x2E / %xA0-%xFF | ASCII: A-Z / a-z / 0-9 / space / ampersand (@) / hyphen / dot / visible characters from Latin-1 |
| nserver-val | %xx41-x5A / %x61-%x7A / %x30-%x39 / %x2D / %x2E / %x3A / %x20 | ASCII: A-Z / a-z / 0-9 / hyphen / dot / colon/ space |

| Applicable Rules |
| address-rule = 1*255(name-val) |
| authinfohash-rule = 64*64(ace-val / digit-val) |
| authinfo-erule = 1*1("true") |
| authinfo-rule = 1*1(authinfo-val) |
| boolean-erule = 1*1("true" / "false") |
| check-erule = 1*1("CHECK") |
| chholder-erule = 1*1("CHHOLDER") |
| chprov-erule = 1*1("CHPROV") |
| city-rule = 1*80(name-val) |
| contact-rule = 9*32"DENIC-" (digit-val / ace-val / %x2E) |
| contactstatus-erule = 1*1("free" / "exists" / "invalid") |
| country-erule = 1*2(ALPHA) Hint |  | The valid list of ISO country codes (country-erule) can be found here: ISO 3166 Country Codes |

Source: <https://docs.denic.de/en/Content/DENIC-29/Datentypen%20und%20Wertebereiche%20f%C3%BCr%20Datenfelder.htm>


## Letter-case conventions for data in requests

| Date | Format | Example |
| DENIC handle | Uppercase | DENIC-1000002-DENIC |
| Domain | Lowercase | de-example.de |
| Name server | Lowercase | ns1.de-example.de |
| NS-Enty | Host name Lowercase, Typ Uppercase | de-example.de IN A 81.91.170.12 |

Source: <https://docs.denic.de/en/Content/DENIC-29/Schreibweisen%20f%C3%BCr%20Daten%20in%20Auftr%C3%A4gen.htm>
