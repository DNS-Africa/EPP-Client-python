#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

Color logging portions: Copyright (C) 2010-2012 Vinay Sajip. All rights reserved. Licensed under the new BSD license.
https://gist.github.com/758430

The rest: © DNS Africa 2016. All rights reserved.

Python logging can go down the rabbit hole very quickly. This module attempts to simplify things somewhat.
Simplest usage:
    enableLogging(debug=True, color=True, console=True, syslog=False)
Otherwise the standard python logging.config.dictConfig is better for more complicated settings.
Eg:

logging_config = {
    'version': 1,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-15s [%(process)s] %(levelname)s (%(filename)s:%(lineno)d) %(message)s'
        },
        'syslog': {
            'class': 'logging.Formatter',
            'format': '%(name)-15s [%(process)s] %(levelname)s (%(filename)s:%(lineno)d) %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'damslib.colorlogging.ColorizingStreamHandlerStdOut'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/tmp/dams.log',
            'mode': 'w',
            'formatter': 'detailed',
        },
        'foofile': {
            'class': 'logging.FileHandler',
            'filename': 'mplog-foo.log',
            'mode': 'w',
            'formatter': 'detailed',
        },
        'errors': {
            'class': 'logging.FileHandler',
            'filename': 'mplog-errors.log',
            'mode': 'w',
            'level': 'ERROR',
            'formatter': 'detailed',
        },
    },
    'loggers': {
        'root': {
            'level': 'DEBUG',
            'handlers': ['console',]
        },
        'foo': {
            'handlers': ['foofile']
        }
    },
}

logging.config.dictConfig(logconfig)

"""
__version__ = "$Id: ColorLogging.py,v default:0 Wed, 25 Mar 2015 15:21:37 +0200 ed $"
__author__ = "Ed Pascoe <ed@dnservices.co.za>"

import ctypes
import logging
import logging.config
import logging.handlers
import os
import sys

log = logging.getLogger('root')

def resetLogging(level=logging.ERROR):
    """Remove all current logging config"""
    logging._acquireLock()
    try:
        logging.root = logging.RootLogger(level)
        logging.Logger.root = logging.root
        logging.Logger.manager = logging.Manager(logging.Logger.root)
    finally:
        logging._releaseLock()

def enableLogging(debug=False, color=True, console=True, syslog=False, forceisatty=False):
  """Turn on logging. Default Loglevel is info. For use when full blown xml base config is overkill.
     Color is only used for console logging.
     The forceisatty will always put out color output.
     Note: this will configure the 'root' logger only. For more complicated usage the dic
  """
  resetLogging() #Wipe out current config
  logging.config.dictConfig({ #Blank any existing logging config
      'version': 1,
  })
  root = logging.getLogger()

  myname = sys.argv[0]
  formatter = logging.Formatter(myname + "[%(process)s] %(levelname)s (%(filename)s:%(lineno)d) %(message)s")

  if console:
      if color:
          if forceisatty:
              conlog = ColorizingStreamHandler(sys.stdout)  # Also force STDOUT (makes pycharms happy)
              conlog.forceisatty = True
          else:
              conlog = ColorizingStreamHandler()
      else: conlog = logging.StreamHandler()
      conlog.setFormatter(formatter)
      root.addHandler(conlog)
  if syslog:
    sl = logging.handlers.SysLogHandler('/dev/log')
    sl.setFormatter(formatter)
    root.addHandler(sl)

  if debug: 
    root.setLevel(logging.DEBUG)
  else:
    root.setLevel(logging.INFO)

  #log.debug("Debug")
  #log.info("info")
  #log.warning("warning")
  #log.error("error")
  #log.critical("critical")

class ColorizingStreamHandler(logging.StreamHandler):
    # color names to indices
    color_map = {
        'black': 0,
        'red': 1,
        'green': 2,
        'yellow': 3,
        'blue': 4,
        'magenta': 5,
        'cyan': 6,
        'white': 7,
    }
    forceisatty = False

    #levels to (background, foreground, bold/intense)
    if os.name == 'nt':
        level_map = {
            logging.DEBUG: (None, 'blue', True),
            logging.INFO: (None, 'green', False),
            logging.WARNING: (None, 'yellow', True),
            logging.ERROR: (None, 'red', True),
            logging.CRITICAL: ('red', 'white', True),
        }
    else: level_map = {
            logging.DEBUG: (None, 'blue', False),
            logging.INFO: (None, 'green', False),
            logging.WARNING: (None, 'yellow', False),
            logging.ERROR: (None, 'red', False),
            logging.CRITICAL: ('red', 'white', True),
        }
    csi = '\x1b['
    reset = '\x1b[0m'

    @property
    def is_tty(self):
        if self.forceisatty:  # Always pretend to be a tty.
            return True
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if not self.is_tty:
                stream.write(message)
            else:
                self.output_colorized(message)
            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    if os.name != 'nt':
        def output_colorized(self, message):
            self.stream.write(message)
    else:
        import re
        ansi_esc = re.compile(r'\x1b\[((?:\d+)(?:;(?:\d+))*)m')

        nt_color_map = {
            0: 0x00,    # black
            1: 0x04,    # red
            2: 0x02,    # green
            3: 0x06,    # yellow
            4: 0x01,    # blue
            5: 0x05,    # magenta
            6: 0x03,    # cyan
            7: 0x07,    # white
        }

        def output_colorized(self, message):
            parts = self.ansi_esc.split(message)
            write = self.stream.write
            h = None
            fd = getattr(self.stream, 'fileno', None)
            if fd is not None:
                fd = fd()
                if fd in (1, 2): # stdout or stderr
                    h = ctypes.windll.kernel32.GetStdHandle(-10 - fd)
            while parts:
                text = parts.pop(0)
                if text:
                    write(text)
                if parts:
                    params = parts.pop(0)
                    if h is not None:
                        params = [int(p) for p in params.split(';')]
                        color = 0
                        for p in params:
                            if 40 <= p <= 47:
                                color |= self.nt_color_map[p - 40] << 4
                            elif 30 <= p <= 37:
                                color |= self.nt_color_map[p - 30]
                            elif p == 1:
                                color |= 0x08 # foreground intensity on
                            elif p == 0: # reset to default color
                                color = 0x07
                            else:
                                pass # error condition ignored
                        ctypes.windll.kernel32.SetConsoleTextAttribute(h, color)

    def colorize(self, message, record):
        if record.levelno in self.level_map:
            bg, fg, bold = self.level_map[record.levelno]
            params = []
            if bg in self.color_map:
                params.append(str(self.color_map[bg] + 40))
            if fg in self.color_map:
                params.append(str(self.color_map[fg] + 30))
            if bold:
                params.append('1')
            if params:
                message = ''.join((self.csi, ';'.join(params),
                                   'm', message, self.reset))
        return message

    def format(self, record):
        message = logging.StreamHandler.format(self, record)
        if self.is_tty:
            # Don't colorize any traceback
            parts = message.split('\n', 1)
            parts[0] = self.colorize(parts[0], record)
            message = '\n'.join(parts)
        return message

class ColorizingStreamHandlerStdOut(ColorizingStreamHandler):
    """The ColorizingStreamHandler but with output to StdOut and forceisatty turned on. (Good for pycharms logging)
    """
    def __init__(self):
        self.forceisatty = True
        super().__init__(sys.stdout)

def maintest():
    print("todo MAINTEST")
    enableLogging(debug=True)
    logging.debug('DEBUG')
    logging.info('INFO')
    logging.warning('WARNING')
    logging.error('ERROR')
    logging.critical('CRITICAL')

if __name__ == '__main__':
    maintest()
