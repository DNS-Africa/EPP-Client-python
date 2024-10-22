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
  -p PORT, --port=PORT  Port to connect to [8443]
  -c CERT, --cert=CERT  SSL certificate to use for authenticated connections
  -s SSLVERSION, --sslversion=SSLVERSION
                        The ssl version identifier {SSLv2, SSLv3, SSLv23,
                        TLSv1}
  --nossl               Do not use SSL
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
```
