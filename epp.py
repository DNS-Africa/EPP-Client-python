#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Sample Python EPP client
"""
© DNS Africa Ltd. 2022-2024. All rights reserved.
"""
__author__ = "Ed Pascoe <ed@dnservices.co.za>, David Kinnes <david@dns.business>"

import logging
import optparse
import os
import os.path
import random
import re
import select
import socket
import ssl
import struct
import sys
import time
from typing import List

from lib import colorlogging

LOGIN_TEMPLATE="""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
   <command>
      <login>
         <clID>%(username)s</clID>
         <pw>%(password)s</pw>
         <options>
            <version>1.0</version>
            <lang>en</lang>
         </options>
         <svcs>
%(svc)s
         <svcExtension>
%(svc_extension)s
         </svcExtension>
         </svcs>
      </login>
      <clTRID>__CLTRID__</clTRID>
   </command>
</epp>"""


class EPPTCPTransport:
    """An epp client transport class. This is just the raw TCP IP protocol. The XML data needs to be handled separately.
       The EPP transport protocol is defined at http://tools.ietf.org/html/rfc5734 it looks complicated but is
       actually very simple and elegant.
       the actual data should be XML data formated according to RFC5730-RFC5733
       No validation of any data takes place in this Class
    """
    sock = None
    _greeting = ""
    packfmt = "!I"

    def __init__(self, host="127.0.0.1", port=3121, cert=None, nogreeting=False):
        """Connect to the EPP server. Server header in self.header"""
        self._isssl = True
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        if cert is not None:
            logging.debug("Loading certificate from %s", cert)
            context.load_cert_chain(cert)
        else:
            logging.debug("Connecting without certificate.")
        self.sock = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host)
        logging.debug(f"Connecting to host {host}:{port}")
        self.sock.connect((host, port))
        logging.debug(f"Connection to host {host}:{port} established")

        if not nogreeting:
            logging.debug(f"Fetching greeting")
            self._greeting = self.get()
            logging.debug(f"Greeting: {self._greeting}")

    def get(self):
        """Get an EPP response """
        header = bytearray()
        rest = bytearray()  # If we get more bytes than we expected.

        while len(header) < 4:
            if self._isssl:
                data = self.sock.recv(4)
                logging.debug("Initial header via TLS. (%s), %s len %s", type(data), data, len(data))
            else:
                data = self.sock.recv(4, 0x40)  # 0x40 is the MSG_WAITALL flag which can only be used on plain sockets
                logging.debug("Initial header no encryption. (%s), %s len %s", type(data), data, len(data))
            if len(data) == 0:
                print("<!-- " +
                      "Did not receive anything from the server or socket timeout. Was the initial login invalid?" + " -->")
                sys.exit(1)
            header = header + data
            if len(header) > 4:
                rest = header[4:]
                header = header[:4]

        bytes1 = struct.unpack(self.packfmt, header)[0]
        logging.debug("Initial header no encryption. (%s), %s Body should be %s bytes", type(header), header, bytes1)

        data = bytearray()  # the buffer
        total = rest  # Initialize with anything extra read while we were getting the header.
        while len(total) < (bytes1 - 4):
            bytesleft = (bytes1 - 4) - len(total)
            data = self.sock.recv(bytesleft)
            length = len(data)
            # length = self.sock.recv_into(data, 16384)
            # logging.debug("Data %s %s", len(data), data)
            if length == 0:
                print("<!-- " +
                      "Could not receive the rest of the expected message header. Only have {0} bytes out of expected {1}.".format(
                          len(total), (bytes1 - 4)) + " -->")
                sys.exit(1)
            total = total + data
        return str(total, 'utf-8')

    def send(self, data: bytes):
        """Send an EPP command """
        # Write the header
        self.sock.sendall(struct.pack('=L', socket.htonl(len(data) + 4)))

        logging.debug('Sending size %s bytes %s' % ((len(data) + 4), struct.pack('=L', socket.htonl(len(data) + 4))))
        # Send the data
        self.sock.sendall(data)
        logging.debug("Sent: %s", data)

    def request(self, data):
        """Convenience function. Does a send and then returns the result of a get. Also converts the string __CLTRID__ to a suitable unique clTRID"""
        cltrid = "EPPTEST-%s.%s" % (time.time(), random.randint(0, 1000000))
        self._lastcltrid = cltrid
        data = data.replace('__CLTRID__', cltrid)
        self.send(bytes(data, encoding='utf8'))
        return self.get()

    def getGreeting(self):
        """Returns the EPP servers greeting"""
        return str(self._greeting)

    def close(self):
        """Close the socket"""
        self.sock.close()


def templatefill(template, defines):
    """Fill out the given template with values as requested"""
    data = {}
    for d in defines:
        p = d.find("=")
        if p == -1:
            print("Unable to interpret definition %s. Aborting!" % (d))
            sys.exit(1)
        k = d[:p]
        v = d[p + 1:]
        data[k] = v
    return template % data


def send_epp(data):
    if options.defs is not None and len(options.defs) > 0:
        data = templatefill(data, options.defs)

    if options.testing:
        print(data)
    else:
        print(epp.request(data))
        print("\n<!-- ================ -->\n")


def eppLogin(username: str, password: str, services: List = None, extensions: List = None):
    """Performs an epp login command. Ignore the services parameter for the co.za namespace."""
    """urn:ietf:params:xml:ns:secDNS-1.1"""
    """['urn:ietf:params:xml:ns:domain-1.0', 'urn:ietf:params:xml:ns:contact-1.0']"""

    # Load the EPP services
    svc = ''
    for service in services:
         svc += f"            <objURI>{service}</objURI>\n"

    # Load the EPP extensions
    svc_ext = ''
    for extension in extensions:
        svc_ext += f"            <extURI>{extension}</extURI>\n"

    data = {'username': username, 'password': password, 'svc': svc, 'svc_extension': svc_ext}
    if options.verbose:
        print(f"Sending Login:\n {LOGIN_TEMPLATE % data}\n")
    result = str(epp.request(LOGIN_TEMPLATE % data))
    if re.search('result code.*1000', result):
        return True  # Good login.
    if re.search('result code.*2002', result):
        return True  # Already logged in.
    else:
        print(result)
        sys.exit(1)


def fileRead(fname):
    """Tries to locate fname and read it in."""
    if not os.path.exists(fname):
        newfname = os.path.join(os.path.dirname(__file__), fname)
        if not os.path.exists(newfname):
            print("Unable to locate file %s. Aborting!" % (fname))
            sys.exit(1)
        else:
            fname = newfname
    return open(fname).read()


if __name__ == "__main__":
    usage = ("Usage:" + " %prog [<options>] <files...>\n"
             + "Example EPP client. The individual EPP commands should be in files specified on the command line.\n"
             + "Eg: docker run --rm -i -v /certs:/certs -c /certs/my_cert_bundle.pem --host=reg-test.dnservices.co.za login.xml create_host.xml create_domain.xml\n"
             + "Will replace all occurances of __CLTRID__  with a suitable clTRID value\n")
    if sys.version_info[0] >= 2 and sys.version_info[1] >= 6:
        usage = usage + __doc__
    # print usage
    # sys.exit(1)
    parser = optparse.OptionParser(usage)
    parser.add_option("--host", "--ip", dest="host", default="127.0.0.1", help="Host to connect to [%default] ")
    parser.add_option("--port", "-p", dest="port", default="3121", help="Port to connect to" + " [%default]")
    parser.add_option("--cert", "-c", dest="cert", help="SSL certificate to use for authenticated connections")
    parser.add_option("--verbose", "-v", dest="verbose", action="store_true", default=False,
                      help="Show the EPP server greeting and other debug info")
    parser.add_option("--username", "-u", dest="username", help=
    "Username to login with. If not specified will assume one of the provided files will do the login.")
    parser.add_option("--password", dest="password", help="Password to login with")
    parser.add_option("--ng", dest="nogreeting", action="store_true", default=False,
                      help="Do not wait for an EPP server greeting")
    parser.add_option("--testing", "-t", dest="testing", action="store_true", default=False,
                      help="Do not connect to the server just output the completed templates")
    parser.add_option("-d", "--define", dest="defs", action="append",
                      help="For scripting, any fields to be replaced (python dictionary subsitution). Eg: -d "
                           "DOMAIN=test.co.za will replace %(DOMAIN)s with test.co.za")
    parser.add_option("--svc", dest="svc", action="append", default=['urn:ietf:params:xml:ns:domain-1.0', 'urn:ietf:params:xml:ns:contact-1.0'],
                      help="Add a services sent with the epp login command "
                           "--svc 'urn:ietf:params:xml:ns:host-1.0'")
    parser.add_option("--svc-ext", dest="svc_ext", action="append", default=['urn:ietf:params:xml:ns:secDNS-1.1'],
                      help="Add a services extensions sent with the epp login command "
                           "--svc-ext 'urn:ietf:params:xml:ns:secDNS-1.1'")
    (options, args) = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
        colorlogging.enableLogging(debug=True, color=True, console=True)
    else:
        logging.basicConfig(level=logging.INFO)
        colorlogging.enableLogging(debug=False, color=True, console=True)

    # Args not necessary
    # if not args:
    #     parser.print_help()
    #     sys.exit(2)

    if not options.testing:
        try:
            if options.cert:
                try:
                    open(options.cert).close()
                except IOError as e:
                    print("Could not read the SSL certificate %s\n%s" % (options.cert, e))
                    sys.exit(1)
                epp = EPPTCPTransport(options.host, int(options.port), cert=options.cert,
                                      nogreeting=options.nogreeting)
            else:
                epp = EPPTCPTransport(options.host, int(options.port), nogreeting=options.nogreeting)
        except ssl.SSLError as e:
            print("Could not connect due to an SSL error")
            print(e)
            sys.exit(1)

        if options.verbose:
            print("<!-- Greeting:-->")
            print(str(epp.getGreeting()))

        if options.username is not None:
            eppLogin(options.username, options.password, options.svc, options.svc_ext)

    # Permit the first xml command file from an input pipe - that will permit flexibility of xml command file pre-processing 
    # Eg. remove comments:
    # cat create_domain.xml | sed -e 's/<!--.*-->//g' -e '/<!--/,/-->/d' | epp.py ...
    if select.select([sys.stdin, ], [], [], 0.0)[0]:
        request_data = sys.stdin.read()
        if len(request_data) > 0:
            if options.verbose:
                print(f"Sending from stdin:\n{request_data}")
            send_epp(request_data)

    for fname in args:
        try:
            if options.verbose:
                logging.debug(f"Sending file {fname}")
            send_epp(fileRead(fname))
        except IOError:
            if not os.path.exists(fname):
                print("The file %s does not exist." % fname)
            else:
                print("Unable to read %s." % fname)
            sys.exit(1)

    if not options.testing:
        epp.close()
