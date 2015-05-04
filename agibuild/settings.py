# -*- coding: utf-8 -*-

""" settings -- global constants """

from os import path, makedirs
import sys

# Current version string
VERSION = '0.3.3'
PROG_NAME = path.basename(sys.argv[0])


def check_var(var):
    expanded = path.expandvars(var)
    if expanded != var:
        return expanded
    return None


HOME_PATH = check_var('$HOME') or path.expanduser('~')
# Path to the user directory
USER_PATH = path.join(check_var('$XDG_CONFIG_HOME') or
                      path.join(check_var('$HOME') or
                                path.expanduser('~'), '.config'),
                      'agibuilder')

# Package base path (where the module script files are located)
PACKAGE_PATH = path.abspath(path.dirname(__file__))

# Path to the configuration file
MAIN_CONFIG_PATH = '/etc/agibuild.conf'
CONFIG_PATH = path.join(USER_PATH, 'config')
LOOPS_PATH = path.join(PACKAGE_PATH, '..', 'loops')

# Log settings
LOG_ERROR_FORMAT = u"%(levelname)s at %(asctime)s in %(funcName)s in \
%(filename)s at line %(lineno)d: %(message)s"
LOG_ERROR_DATE = u'[%d.%m.%Y %I:%M:%S]'
LOG_DEBUG_FORMAT = u'%(asctime)s: %(message)s'
# LOG_ERROR_FORMAT = LOG_DEBUG_FORMAT
LOG_PATH = path.join(USER_PATH, 'log')
LOG_CONFIG = {
    'version': 1,
    'formatters': {
        'error': {
            '()': 'agibuild.uformatter.UnicodeFormatter',
            'format': LOG_ERROR_FORMAT,
            'datefmt': LOG_ERROR_DATE
        },
        'debug': {
            '()': 'agibuild.uformatter.UnicodeFormatter',
            'format': LOG_DEBUG_FORMAT,
            'datefmt': u'[%d %b %I:%M:%S]'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'debug', 'level': 'DEBUG'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH+'.out', 'maxBytes': 100000,
            'backupCount': 5, 'formatter': 'error', 'level': 'ERROR'
        }
    },
    'root': {'handlers': ('console', 'file'), 'level': 'DEBUG'}
}


BLACKLIST_PACKAGES = ["aaa_elflibs", "aaa_base", "aaa_terminfo",
                      "aaa_elflibs_dummy"]
BLACKLIST_LOOPS = ['.', '..']

ABUILD_PATH = path.join(HOME_PATH, 'abuilds')
GIT_CACHE_DIR = "/tmp/agibuild/git"
SCRIPT_PATH = "./scripts/"
STYLES_PATH = "./styles/"
NUMERATE = False

if not path.exists(USER_PATH):
    makedirs(USER_PATH)


def opt(var, default=False):
    try:
        return globals()[var.upper()]
    except KeyError:
        return default


# Load logging
import logging
try:
    from logging.config import dictConfig
except ImportError:
    from .dictconfig import dictConfig
dictConfig(LOG_CONFIG)

# Set hook
# from builder.utils import excepthook
# sys.excepthook = excepthook
