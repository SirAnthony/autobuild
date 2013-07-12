# -*- coding: utf-8 -*-

import os, getopt, sys
import json
from . import settings
from . import options
from .output import set_level, error as _e
import re


def usage(name):
    try:
        options.usage(name)
    except:
        pass
    sys.exit(2)



def options_parse(prog, version, argv):
    """
    Return options found in argv.
    prog will be to usage() when --help is requested.
    version will be printed for --version.
    The first items of argv must be an option, not the executable name like
    in sys.argv!
    The result has the format {section: {option: value}}
    """
    try:
        opts, args = getopt.getopt(argv, options.GETOPT_SHORT,
                                         options.GETOPT_LONG)
    except getopt.GetoptError, err:
        _e(err)
        usage(prog)

    if not args:
        usage(prog)

    processed = {}
    for o, a in opts:
        if not o:
            continue

        if o in ('-h', '--help'):
            usage(prog)
        elif o == '--debug':
            set_level('debug')

        name, opt = options.SHORT.get(o,
                    options.LONG.get(o, (None, None)))
        tgt = CL_OPTS if name in options.CL else processed
        tgt[name] = a if opt else True
    return processed, args


def extend_settings(args):
    if not args:
        return

    config_dict = {}
    config_path = args.get('config_path') or default_opts.get('config_path') \
                    or settings.CONFIG_PATH

    for filename in (settings.MAIN_CONFIG_PATH, config_path):
        try:
            with file(filename, 'rU') as stream:
                config_dict.update(json.load(stream))
        except:
            pass

    if 'config_path' in config_dict:
        _e('Cannot rewrite config path in config file')
        del config_dict['config_path']

    extdict = dict(default_opts, **config_dict)
    extdict.update(args)
    for key, value in extdict.items():
        setattr(settings, key.upper(), value)


def parse_input(args):
    packages = []
    for item in args:
        if os.path.isfile(item):
            with open(item, 'rU') as fl:
                names = fl.readlines()
            packages.extend(filter(None, [
                re.sub('#.*', '', name).strip() for name in names]))
        else:
            packages.append(item)
    return packages

def clopt(name, default=None):
    return CL_OPTS.get(name, default)


default_opts = {
    'path': '',
}

CL_OPTS = {}

run_opts, run_args = options_parse(os.path.basename(sys.argv[0]),
                            settings.VERSION, sys.argv[1:])
extend_settings(run_opts)
package_list = parse_input(run_args)


__all__ = ['run_opts', 'run_args', 'packages_list', 'clopt']
