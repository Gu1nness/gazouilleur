#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, traceback
import logging as log
from gazouilleur import config
from .colorize import colorize

logg.getLogger("asyncio").setLevel(logging.INFO)

COLOR_LOGS = (str(getattr(config, "COLOR_LOGS", "true")).lower() == "true")
def colr(text, color, bold=True):
    if COLOR_LOGS:
        return colorize(text, color, style='bold' if bold else '')
    return text

def _logg(text, color=None, error=False):
    if color:
        text = colr(text, color)
    elif error:
        text = colr("ERROR %s" % text, 'red')
    return text

def _context(channel=None, action=None, debug=True):
    tmp = ""
    if debug:
        tmp += colr("DEBUG", 'magenta')
        if channel or action:
            tmp += ":"
    if action:
        tmp += colr(action, 'green')
    if channel and action:
        tmp += "/"
    if channel:
        tmp += colr(channel, 'blue')
    return tmp

def logg(text, color=None, channel=None, action=None, error=False, debug=False):
    try:
        return log.info(_logg(text, color, error))
    except UnicodeDecodeError as e:
        print "WARNING: weird UnicodeDecodeError detected"
        traceback.print_stack()
        return log.msg(text, system=_context(channel, action, debug))

def loggirc(text, chan=None):
    if chan:
        chan = chan.replace('*', '')
    return logg(text, color="cyan", action="IRC", channel=chan)

def loggirc2(text, chan=None):
    return logg(text, color="magenta", action="IRC", channel=chan)

def loggerr(text, chan=None, action=None):
    return logg(text, error=True, action=action, channel=chan)

def loggvar(text, chan=None, action=None):
    return logg(text, color="yellow", action=action, channel=chan)

def logerr(text):
    return sys.stderr.write(_logg("%s\n" % text, error=True))

def debug(text, chan=None, action=None):
    return logg(text, color="green", action=action, channel=chan, debug=True)
