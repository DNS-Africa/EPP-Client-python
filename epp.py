#!/usr/bin/env python2
__version__ = "$Id$"
__author__ = "Ed Pascoe <ed@dnservices.co.za>, David Peall <david@dns.business>, Theo Kramer <theo@dns.business>"

import gettext
import logging
import optparse # brain dead python2 argument parser - replace with argparse
import os
from os import isatty
import os.path
import random
import re
import socket
import ssl
import struct
import sys
import time
import select

# from lib import colorlogging

# From chatgpt https://chat.openai.com - provide python3 code to insert at the start of every function to list the name of the function and the arguments passed to the function
def log_function_call(func):
    def wrapper(*args, **kwargs):
        if options.testing:
            # print(f"Function Name: {func.__name__}")
            print("Function Name: %s" % (func.__name__))
            # print(f"Arguments: {args} {kwargs}")
            print("Arguments: %s" % (args, kwargs))
        result = func(*args, **kwargs)
        return result
    return wrapper

# @log_function_call
# def my_function(arg1, arg2, kwarg1=None, kwarg2=None):
#     # Function body goes here
#     pass

# Enable translation
t = gettext.translation('rye', os.path.join(os.path.dirname(__file__), 'locale'), fallback=True)
_ = t.gettext

log = logging.getLogger()

packfmt = "!I"

# TK Wed May 31 13:18:08 SAST 2023 FROM /home/coza/regression/EPP/TCPTransport - use TCPTransport class instead of EPPTCPTransport class

# From  /home/coza/regression/EPP/TCPTransport.py
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
def _sslProtoByName(protocol=None):
  """Returns the ssl protocol number given a protocol name.
     Correctly handles protocol already being a protocol number.
     If protocol is None TLSv1 is assumed.
    
  """
  protocol_list = list([x[len('PROTOCOL_'):] for x in dir(ssl) if x.find("PROTOCOL_") == 0 ] ) #Generate a list of protocols from the ssl module.
  log.debug("Given ssl protocol '%s' is one of %s" % (protocol, ", ".join(protocol_list)))

  if isinstance(protocol, int): #Already converted to a protocol number.
    return protocol  
  if protocol is None:
    return ssl.PROTOCOL_TLSv1
  try:
    return getattr(ssl, "PROTOCOL_"+str(protocol))
  except AttributeError:
    protocol_list = list([x[len('PROTOCOL_'):] for x in dir(ssl) if x.find("PROTOCOL_") == 0 ] ) #Generate a list of protocols from the ssl module.
    raise AttributeError("Given ssl protocol '%s' is not and integer or one of %s" % (protocol, ", ".join(protocol_list)))

class TCPTransportError(Exception):
  """Errors from EPPTCPTransport"""

class TCPTransport:
  """An epp client transport class. This is just the raw TCP IP protocol. The XML data needs to be handled separately.
     The EPP transport protocol is defined at http://tools.ietf.org/html/rfc5734 it looks complicated but is 
     actually very simple and elegant. 
     the actual data should be XML data formated according to RFC5730-RFC5733
     No validation of any data takes place in this Class
  """
  sock = None
  sock_host = ""
  sock_port = 0
  _greeting = ""
  _isssl = None
  _timeout = 5

  def __init__(self, host="127.0.0.1", port=3121, usessl=True, cert=None, nogreeting=False, ssl_version=ssl.PROTOCOL_TLSv1):
    """Connect to the EPP server. Server header in self.header, """
    socket.setdefaulttimeout(self._timeout)
    if usessl:
      self._isssl = True
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      ssl_version= _sslProtoByName(ssl_version)
      # do not require a certificate from the server
      self.sock = ssl.wrap_socket(s, cert_reqs=ssl.CERT_NONE, certfile=cert, ssl_version=ssl_version)
      try:
        self.sock.connect((host, port))
      except:
        print "Failed to connect to EPP server %s on port %s. Is the server off line?" % (host, port)
        sys.exit(1)
    else:
      self._isssl = False
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.connect((host, port))
    if not nogreeting:
      self._greeting = self.get()

    self.sock_host = host
    self.sock_port = port
    log.debug("Connected to server '%s:%d'" % (self.sock_host, self.sock_port))

  def get(self):
    """Get an EPP response """
    header = ""
    rest =  "" #If we get more bytes than we expected.
    
    self.sock.settimeout(self._timeout)
    self.sock.setblocking(False)
    tries = 5
    loopCount = 0

    while len(header) < 4:
      if self._isssl:
        data = self.sock.recv(4)
      else:
        data = self.sock.recv(4, 0x40) #0x40 is the MSG_WAITALL flag which can only be used on plain sockets

      if len(data) == 0:
        if loopCount >= tries:
          raise TCPTransportError(_("Did not receive anything from server '%s:%d' or socket timeout. Was the initial login invalid?" % (self.sock_host, self.sock_port)))
        else:
          time.sleep(0.5) # sleep 500 millisecs
          loopCount += 1
          continue
        
      header = header + data
      if len(header) > 4: 
        rest = header[4:]
        header = header[:4]

    bytes1 = struct.unpack(packfmt,header)[0]

    if self._isssl:
      data = [] #the buffer
      total = rest #Initialize with anything extra read while we were getting the header.
      while len(total) < (bytes1-4):
        length = self.sock.recv_into(data, 16384)
        if length == 0:
          # Are the next 2 necessary ?
          # self.sock.settimeout(None)
          # self.sock.setblocking(True)
          raise TCPTransportError(_("Could not receive the rest of the expected message header. Only have {0} bytes out of expected {1}.").format(len(total), (bytes1-4)))

        total += "".join(data[:length])
    else:
      total = self.sock.recv((bytes1-4), 0x40)

    # Are the next 2 necessary ?
    # self.sock.settimeout(None)
    # self.sock.setblocking(True)
    return total # String - bad choice of var name

  def send(self, data):
    """Send an EPP command """
    #Write the header
    self.sock.send(struct.pack(packfmt, int(len(data)+4)))
    #Send the data
    self.sock.send(data)

  def request(self, data):
    """Convenience function. Does a send and then returns the result of a get"""
    self.send(data)
    return self.get()

  def getGreeting(self):
    """Returns the EPP servers greeting"""
    return self._greeting

  def close(self):
    """Close the socket"""
    log.debug("Socket close requested")
    self.sock.close()

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# From  /home/coza/regression/EPP/TCPTransport.py - replaces the following

class EPPTCPTransport:
    """An epp client transport class. This is just the raw TCP IP protocol. The XML data needs to be handled separatly.
       The EPP transport protocol is definied at http://tools.ietf.org/html/rfc5734 it looks complicated but is
       actually very simple and elegant.
       the actual data should be XML data formated according to RFC5730-RFC5733
       No validation of any data takes place in this Class
    """
    sock = None
    _greeting = ""
    _isssl = None

    def __init__(self, host="127.0.0.1", port=3121, usessl=True, cert=None, nogreeting=False):
        """Connect to the EPP server. Server header in self.header"""
        log.debug("EPPTCPTransport.__init__ (host = %s, port = %d, usessl = %s, cert = %s, nogreeting = %s)", host, port, usessl, cert, nogreeting)
        if usessl:
            self._isssl = True
            # TK Wed May 31 12:30:20 SAST 2023 - https://stackoverflow.com/questions/28228214/ssl-module-object-has-no-attribute-sslcontext
            # context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context = ssl.create_default_context()
            context.check_hostname = False
            if cert:
                context.load_cert_chain(cert) #'/u/elp/test/epp/dnservices.pem') #certfile="cert.crt", keyfile="cert.key")
            else: # TK Wed May 31 12:30:20 SAST 2023 - 0x40 causes
                context.verify_mode=ssl.CERT_NONE
            self.sock = context.wrap_socket(socket.socket(socket.AF_INET))
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.connect((host, port))

        if not nogreeting:
            self._greeting = self.get()

    def get(self):
        """Get an EPP response """
        header = bytearray()
        rest = bytearray()  # If we get more bytes than we expected.

        while len(header) < 4:
            if self._isssl:
                data = self.sock.recv(4)
                log.debug("Initial header via TLS. (%s), %s len %s", type(data), data, len(data))
            else:
                # TK Wed May 31 12:30:20 SAST 2023 - 0x40 causes
                #
                # Traceback (most recent call last):
                #   File "/home/theo/bin/epp2.py", line 274, in <module>
                #     epp = EPPTCPTransport(options.host, int(options.port), not options.nossl, nogreeting=options.nogreeting)
                #   File "/home/theo/bin/epp2.py", line 73, in __init__
                #     self._greeting = self.get()
                #   File "/home/theo/bin/epp2.py", line 85, in get
                #     data = self.sock.recv(4, 0x40)  # 0x40 is the MSG_WAITALL flag which can only be used on plain sockets
                # socket.error: [Errno 11] Resource temporarily unavailable
                # data = self.sock.recv(4, 0x40)  # 0x40 is the MSG_WAITALL flag which can only be used on plain sockets
                data = self.sock.recv(4)  # 0x40 is the MSG_WAITALL flag which can only be used on plain sockets
                log.debug("Initial header no encryption. (%s), %s len %s", type(data), data, len(data))
            if len(data) == 0:
                print("<!-- " + _(
                    "Did not receive anything from the server or socket timeout. Was the initial login invalid?") + " -->")
                sys.exit(1)
            header = header + data
            if len(header) > 4:
                rest = header[4:]
                header = header[:4]

        bytes1 = struct.unpack(packfmt, header)[0]
        log.debug("Initial header no encryption. (%s), %s Body should be %s bytes", type(header), header, bytes1)

        data = bytearray()  # the buffer
        total = rest  # Initialize with anything extra read while we were getting the header.
        while len(total) < (bytes1 - 4):
            bytesleft = (bytes1 - 4) - len(total)
            data = self.sock.recv(bytesleft)
            length = len(data)
            #length = self.sock.recv_into(data, 16384)
            #log.debug("Data %s %s", len(data), data)
            if length == 0:
                print("<!-- " + _(
                    "Could not receive the rest of the expected message header. Only have {0} bytes out of expected {1}.").format(
                    len(total), (bytes1 - 4)) + " -->")
                sys.exit(1)
            total = total + data
        return str(total,'utf-8')

    # def send(self, data: bytes):
    def send(self, data):
        """Send an EPP command """
        # Write the header
        self.sock.write(struct.pack('=L', socket.htonl(len(data) + 4)))

        log.debug('Sending size %s bytes %s' % ((len(data) + 4),struct.pack('=L', socket.htonl(len(data) + 4))))
        # Send the data
        self.sock.write(data)
        log.debug("Sent: %s", data)

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


@log_function_call  # decorator to list function name and arguments
def templatefill(template, defines, kwarg1=None, kwarg2=None):
    """Fill out the given template with values as requested"""
    data = {}
    for d in defines:
        p = d.find("=")
        if p == -1:
            print("templatefill(): Unable to interpret definition %s. Aborting!" % (d))
            sys.exit(1)
        k = d[:p]
        v = d[p + 1:]
        data[k] = v
    retTemplate = template
    try:
        retTemplate = template % data
    except KeyError as e:
        print("templatefill(): Replacement value for key %s not defined." % (e))
    except ValueError as ve:
        print("templatefill(): Key name error on one of the replacement keys (%s) in the input text. The key format must conform to '%%s(key)s'" % (defines))
        print("templatefill(): The associated error is '%s'" % (ve))
    finally:
        return retTemplate
    pass

def send_epp(data):
    if options.defs is not None and len(options.defs) > 0:
          data = templatefill(data, options.defs)
    if options.testing:
        print(data)
    else:
        print(epp.request(data))
        print("\n<!-- ================ -->\n")

def eppLogin(username, password, services=['urn:ietf:params:xml:ns:domain-1.0', 'urn:ietf:params:xml:ns:contact-1.0']):
    """Performs an epp login command. Ignore the services parameter for the co.za namespace."""
    template = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
   <command>
      <login>
         <clID>%(username)s</clID>
         <pw>%(password)s</pw>
         <options>
            <version>1.0</version>
            <lang>en</lang>
         </options>
         <svcs>"""
    for svc in services:
        template = template + "            <objURI>%s</objURI>\n" % (svc)
    template = template + """
         </svcs>
      </login>
      <clTRID>__CLTRID__</clTRID>
   </command>
</epp>"""
    data = {'username': username, 'password': password}
    result = str(epp.request(template % data))
    if re.search('result code.*1000', result): return True  # Good login.
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
    usage = (_("Usage:") + " %prog [<options>] <files...>\n" +
             _("Example EPP client. The individual EPP commands should be in files specified on the command line.\n")
             + _("Eg: ./epp2.py --host=reg-test.dnservices.co.za login.xml create_host.xml create_domain.xml\n")
             + _("or: cat create_domain.xml | ./epp2.py --host=reg-test.dnservices.co.za -p 3121 -u uniforum --password=PASSWORD  -d DOMAIN=uniforum.co.za # where '%(DOMAIN)s' in create_domain.xml is replaced with 'uniforum.co.za' and the login is handled internally using EPP login credentials defined by '-u' and '--password' \n")
             + _("Will replace all occurances of __CLTRID__  with a suitable clTRID value\n"))
    # if sys.version_info[0] >= 2 and sys.version_info[1] >= 6:
    #     usage = usage + __doc__
    # print usage
    # sys.exit(1)
    parser = optparse.OptionParser(usage)
    parser.add_option("--host", "--ip", dest="host", default="127.0.0.1", help=_("Host to connect to [%default] "))
    parser.add_option("--port", "-p", dest="port", default="3121", help=_("Port to connect to") + " [%default]")
    parser.add_option("--cert", "-c", dest="cert", help=_("SSL certificate to use for authenticated connections"))
    parser.add_option("--nossl", dest="nossl", action="store_true", default=False, help=_("Do not use SSL"))
    parser.add_option("--verbose", "-v", dest="verbose", action="store_true", default=False,
                      help=_("Show the EPP server greeting and other debug info"))
    parser.add_option("--username", "-u", dest="username", help=_(
        "Username to login with. If not specified will assume one of the provided files will do the login."))
    parser.add_option("--password", dest="password", help=_("Password to login with"))
    parser.add_option("--ng", dest="nogreeting", action="store_true", default=False,
                      help=_("Do not wait for an EPP server greeting"))
    parser.add_option("--testing", "-t", dest="testing", action="store_true", default=False,
                      help=_("Do not connect to the server just output the completed templates"))
    parser.add_option("-d", "--define", dest="defs", action="append",
                      help=_("For scripting, any fields to be replaced (python dictionary subsitution). Eg: -d "
                             "DOMAIN=test.co.za will replace %(DOMAIN)s with test.co.za"))
    (options, args) = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
        # colorlogging.enableLogging(debug=True, color=True, console=True)
    else:
        logging.basicConfig(level=logging.INFO)
        # colorlogging.enableLogging(debug=False, color=True, console=True)

    # Args not necessary if piping an EPP xml command into epp.py
    inputFromStdin = False
    if isatty(sys.stdin.isatty()):
    # if select.select([sys.stdin, ], [], [], 0.0)[0]:
        inputFromStdin = True
        if not args:
            parser.print_help()
            sys.exit(2)

    if not options.testing:
        try:
            if options.cert:
                try:
                    open(options.cert).close()
                except IOError as e:
                    print("Could not read the SSL certificate %s\n%s" % (options.cert, e))
                    sys.exit(1)
                # epp = EPPTCPTransport(options.host, int(options.port), usessl=not options.nossl, cert=options.cert,
                #                       nogreeting=options.nogreeting)
                epp = TCPTransport(options.host, int(options.port), usessl=not options.nossl, cert=options.cert,
                                   nogreeting=options.nogreeting)
            else:
                # epp = EPPTCPTransport(options.host, int(options.port), not options.nossl, nogreeting=options.nogreeting)
                epp = TCPTransport(options.host, int(options.port), not options.nossl, nogreeting=options.nogreeting)
        except ssl.SSLError as e:
            print("Could not connect due to an SSL error")
            print(e)
            sys.exit(1)

        if options.verbose:
            print("<!-- Greeting:-->")
            print(str(epp.getGreeting()))

        if options.username is not None:
            eppLogin(options.username, options.password)

    # Permit the first xml command file from an input pipe - that will permit flexibility of xml command file pre-processing 
    # Eg. remove comments:
    # cat create_domain.xml | sed -e 's/<!--.*-->//g' -e '/<!--/,/-->/d' | epp.py ...

    # print(_("Args are:- %s") % (args))

    if select.select([sys.stdin, ], [], [], 0.0)[0]:
    # if inputFromStdin == True:
        send_epp(sys.stdin.read())
        # print(sys.stdin.read())

    # print(_("Args are:- %s") % (args))
    # sys.exit(1)

    for fname in args:
        try:
            send_epp(fileRead(fname))
        except IOError:
            if not os.path.exists(fname):
                print(_("The file %s does not exist.") % fname)
            else:
                print(_("Unable to read %s.") % fname)
            sys.exit(1)

    if not options.testing:
        epp.close()
