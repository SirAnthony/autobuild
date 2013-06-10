# -*- coding: utf-8 -*-

import logging

"""Options module
This module holds all options program have
Options format:
    (short_name, long_name, description, return_name, arguments_count, processing_callback)

Callback function may be anything, but if it returns False
program execution stops after call of this functuin
"""


def usage(prog_name, *args, **kwargs):
    print """\
Usage:  [{0}] filename
        [{0}] package1, package2, package3, ...

""".format(GETOPT_SHORT)
    for item in OPTIONS:
        print "\t-{0} --{1}\t\t{2}".format(*item)

def opt(name, mod, char):
    return '{0}{1}'.format(name, '' if not mod else char)


CL_OPTS = (
    ('h', 'help', 'Show this help message and exit', None, 0),
    ('n', 'numerate', 'Numerate arrays items', 'numerate', 0),
    ('o', 'list-order', 'Only caclulate package order and exit',
        'list_order', 0),
    ('s', 'start-from', 'Specify the index of package to start building. \
All preceding packages will be skipped', 'start_from', 1),
    ('g', 'make-graph', 'Generate dependency graph', 'graph_path', 1),
    ('G', 'highlight-graph', 'Highlight packages in graph. Only usable with -g',
        'highlight_graph', 1)
)

SETTINGS_OPTS = (
    ('t', 'abuilds-tree', 'Specify path to directory with abuilds',
        'abuild_path', 1),
    ('m', 'ignore-missing', 'Ignore missing packages',
        'ignore_missing', 0),
    ('r', 'no-rebuild-installed', 'Does not rebuild packages must be installed',
        'no_rebuild_installed', 0),
    ('c', 'skip-failed', 'Continue if some packages failed to build',
        'skip_failed', 0),
    ('I', 'no-install', 'Does not install packages after build',
        'no_install', 0)
)


OPTIONS = CL_OPTS + SETTINGS_OPTS


SHORT = dict([('-{0}'.format(x[0]), x[-2:]) for x in OPTIONS])
LONG = dict([('--{0}'.format(x[1]), x[-2:]) for x in OPTIONS])
GETOPT_SHORT = ''.join([opt(x[0], x[-1], ':') for x in OPTIONS])
GETOPT_LONG = [opt(x[1], x[-2], '=') for x in OPTIONS]
CL = [opt[4] for opt in CL_OPTS]



__all__ = ['usage', 'OPTIONS', 'SHORT', 'LONG',
           'GETOPT_SHORT', 'GETOPT_LONG', 'CL']
