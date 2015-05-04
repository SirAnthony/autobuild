# -*- coding: utf-8 -*-

from . import settings
from .adict import AttrDict
import json
import logging

BASE_COLORS = {
    'default': '\033[39m',
    'black': '\033[30m',
    'red': '\033[31m',
    'dgreen': '\033[32m',
    'dyellow': '\033[33m',
    'dblue': '\033[34m',
    'dmagenta': '\033[35m',
    'dcyan': '\033[36m',
    'dgray': '\033[90m',
    'gray': '\033[37m',
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
}


BASE_FORMATTING = {
    'end': '\033[0m', # Reset
    'bold': '\033[1m',
    'dim': '\033[2m',
    'underline': '\033[4m',
    'blink': '\033[5m',
    'reverse': '\033[7m',
    'hidden': '\033[7m',
}


EXTENDED_COLORS = {
  'version': '\033[93m', # light yellow
  'old_version': '\033[95m', # light magneta
  'miss_dep': '\033[96m', # light cyan
  'install': '\033[94m', # light blue
  'build': '\033[92m', # light green
  'missing': '\033[91m', # light red
  'keep': '\033[37m', #light gray
}


COLORS = AttrDict(BASE_COLORS.items() + BASE_FORMATTING.items() + EXTENDED_COLORS.items())
NO_COLORS = AttrDict([(key, '') for key in COLORS.keys()])


def set_level(l):
    level = logging.INFO
    if l == 'debug':
        level = logging.DEBUG
    root_logger = logging.getLogger()
    root_logger.setLevel(level)


def force_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    if isinstance(s, unicode):
        return s
    try:
        if not isinstance(s, str):
            if hasattr(s, '__unicode__'):
                s = s.__unicode__()
            else:
                s = unicode(bytes(s), encoding, errors)
        else:
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise
        else:
            s = ' '.join([force_unicode(arg, encoding, strings_only,
                    errors) for arg in s])
    return s



def gettext(text):
    """Localisation hook"""
    return force_unicode(text)



def resolve(text, *args, **kwargs):
    """Format text using arguments and colorize it if needed."""
    text = gettext(text)
    # Allways close formatting
    text += '{c.end}{c.default}'
    colors = NO_COLORS
    if not settings.opt('no_color'):
        colors = COLORS
    return text.format(*args, c=colors, **kwargs)



def debug(text, *args, **kwargs):
    """Print message to debug output"""
    logging.debug(resolve(text, *args, **kwargs))


def warn(text, *args, **kwargs):
    """Print message to warning output"""
    logging.warning(resolve(text, *args, **kwargs))


def info(text, *args, **kwargs):
    """Print message to info output"""
    logging.info(resolve(text, *args, **kwargs))


def error(text, e=None, *args, **kwargs):
    """
    Print message to error output.
    Accept exception class as second parameter
    Returns exception object.
    """
    resolved = resolve(text, *args, **kwargs)
    logging.error(resolved)
    return e(resolved) if e else None


set_level('')
