# -*- coding: utf-8 -*-

import os, getopt, sys
import json
from builder import settings
from builder.options import (opt_help, short_opts, long_opts,
                            SHORT_OPTIONS, LONG_OPTIONS, StopExecution)
from utils import AttrDict
import re
import logging


def usage(name):
    try:
        opt_help(name)
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
        opts, args = getopt.getopt(argv, short_opts(), long_opts())
    except getopt.GetoptError, err:
        logging.error(err)
        usage(prog)

    if not args:
        usage(prog)

    processed = {}
    for o, a in opts:
        name, opt, callback = SHORT_OPTIONS.get(o,
                        LONG_OPTIONS.get(o, (None, None, opt_help)))

        try:
            arg = callback(prog, a)
        except StopExecution:
            return False
        except TypeError:
            arg = a if opt else True

        if name:
            processed[name] = arg
    return processed, args


def extend_settings(args):
    if not args:
        return

    config_dict = {}
    config_path = args.get('config_path') or default_opts.get('config_path') \
                    or settings.CONFIG_PATH

    try:
        with file(config_path, 'rU') as stream:
            config_dict = json.load(stream)
    except:
        pass

    if 'config_path' in config_dict:
        logging.error('Cannot rewrite config path in config file')
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



default_opts = {
    'path': '',
}


run_opts, run_args = options_parse(os.path.basename(sys.argv[0]),
                            settings.VERSION, sys.argv[1:])
extend_settings(run_opts)
package_list = parse_input(run_args)


__all__ = ['run_opts', 'run_args', 'packages_list']
