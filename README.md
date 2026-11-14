# Simple Python EPP Client

An epp client transport class. This is just the raw TCP IP protocol. The XML data needs to be handled separately.
The EPP transport protocol is defined at http://tools.ietf.org/html/rfc5734 it looks complicated but is
actually very simple and elegant.

The actual data should be XML data formated according to RFC5730-RFC5733
No validation of any data takes place in this Class

## Usage:

### Getting the image

The image is publicly available
```shell
docker pull dnsbusiness/epp-client:dev
```

### Operating modes
#### Specifying list of template files:
```shell
docker run --rm -v /templates:/templates dnsbusiness/epp-client:dev /templates/first_command.xml
```

#### Pipe XML data from stdin:
```shell
cat templates/domain_info.xml | docker run -i dnsbusiness/epp-client:dev 
```

### Using certificate:
To access certificate files you will need to map the directrory or file into the image using -v.  Multiple -v arguments are possible.
```shell
docker run --rm -i -v /certs:/certs dnsbusiness/epp-client:dev -c /certs/mycert.crt
```

### Other options:

```shell
Options:
  -h, --help            show this help message and exit
  --host=HOST, --ip=HOST
                        Host to connect to [127.0.0.1]
  -p PORT, --port=PORT  Port to connect to [3121]
  -c CERT, --cert=CERT  SSL certificate to use for authenticated connections
  -v, --verbose         Show the EPP server greeting and other debug info
  -u USERNAME, --username=USERNAME
                        Username to login with. If not specified will assume
                        one of the provided files will do the login.
  --password=PASSWORD   Password to login with
  --ng                  Do not wait for an EPP server greeting
  -t, --testing         Do not connect to the server just output the completed
                        templates
  -d DEFS, --define=DEFS
                        For scripting, any fields to be replaced (python
                        dictionary subsitution). Eg: -d DOMAIN=test.co.za will
                        replace %(DOMAIN)s with test.co.za
  --svc=SVC             Add a services sent with the epp login command --svc
                        'urn:ietf:params:xml:ns:host-1.0'. Default if not
                        given: urn:ietf:params:xml:ns:domain-1.0
                        urn:ietf:params:xml:ns:contact-1.0. Use --svc= (empty)
                        first to clear the defaults and send only the services
                        listed after it (e.g. for Google/Nomulus which rejects
                        contact-1.0 with 2307).
  --svc-ext=SVC_EXT     Add a services extensions sent with the epp login
                        command --svc-ext 'urn:ietf:params:xml:ns:secDNS-1.1'.
                        Default if not given:
                        urn:ietf:params:xml:ns:secDNS-1.1. Use --svc-ext=
                        (empty) first to clear the defaults.

### Google / Nomulus registries (contact-1.0 not accepted)

Google removed the contact object with the Minimum Data Set migration; a
`<login>` that declares `contact-1.0` is rejected with 2307. Replace the
default service list instead of extending it:

```shell
docker run --rm -i -v ./keys:/keys dnsbusiness/epp-client:pol1197 \
  --host=epp.registry-sandbox.google --port=700 -c /keys/google_ry_ote.pem \
  -u dnsafrica-3 --password='****' \
  --svc= --svc=urn:ietf:params:xml:ns:domain-1.0 --svc=urn:ietf:params:xml:ns:host-1.0 \
  --svc-ext= --svc-ext=urn:ietf:params:xml:ns:secDNS-1.1 \
  --svc-ext=urn:ietf:params:xml:ns:epp:fee-1.0 \
  /keys/domain_info.xml
```

Use the `--svc=` / `--svc-ext=` (empty) form in scripts that pass flags
through ssh — a bare `''` argument can be lost by shell quoting.
```
