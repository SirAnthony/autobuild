# -*- coding: utf-8 -*-

import sys

"""Options module
This module holds all options program have
Options format:
    (short_name, long_name, description, internal_name, arguments_count)

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
    sys.exit(2)

def opt(name, mod, char):
    return '{0}{1}'.format(name, '' if not mod else char)

# TODO: rename options

CL_OPTS = (
    ('h', 'help', 'Show this help message and exit', None, 0),
    ('n', 'numerate', 'Numerate arrays items', 'numerate', 0),
    ('o', 'list-order', 'Only caclulate package order and exit',
        'list_order', 0),
    ('s', 'start-from', 'Specify the index of package to start building. \
All preceding packages will be skipped', 'start_from', 1),
    ('g', 'make-graph', 'Generate dependency graph', 'graph_path', 1),
    ('G', 'highlight-graph', 'Highlight packages in graph. Only usable with -g',
        'highlight_graph', 1),
    ('d', 'with-build-deps', 'Select all packages which require target packages',
        'build_deps', 0),
    ('p', 'with-deps-only', 'Stop if packages has no deps', 'with_deps', 0),
    ('u', 'update', 'Update installed packages.', 'update', 0),
    ('U', 'enable-vcs', 'Enable treating vcs as updates.', 'enable_vcs', 0),
    ('k', 'build-keep', 'Rebuild packages which will be keep.', 'build_keep', 0),
    ('K', 'show-keep', 'Show packages which will be keep.', 'show_keep', 0),
    ('i', 'skip-install', 'Does not install anything before build.', 'skip_install', 0),
    ('v', 'debug', 'Print debug information.', 'debug', 0),
)

SETTINGS_OPTS = (
    ('a', 'ask', 'Wait for user desigion to build packages', 'ask', 0),
    ('t', 'abuilds-tree', 'Specify path to directory with abuilds',
        'abuild_path', 1),
    ('m', 'ignore-missing', 'Ignore missing packages',
        'ignore_missing', 0),
    ('R', 'no-rebuild-installed', 'Does not rebuild packages must be installed',
        'no_rebuild_installed', 0),
    ('f', 'skip-failed', 'Continue if some packages failed to build',
        'skip_failed', 0),
    ('I', 'no-install', 'Does not install packages after build',
        'no_install', 0),
    ('C', 'no-color', 'Disable colors of output', 'no_color', 0),
    ('D', 'with-deps-print', 'Print packages depend on current package', 'print_depends', 0)
)


OPTIONS = CL_OPTS + SETTINGS_OPTS


SHORT = dict([('-{0}'.format(x[0]), x[-2:]) for x in OPTIONS])
LONG = dict([('--{0}'.format(x[1]), x[-2:]) for x in OPTIONS])
GETOPT_SHORT = ''.join([opt(x[0], x[-1], ':') for x in OPTIONS])
GETOPT_LONG = [opt(x[1], x[-2], '=') for x in OPTIONS]
CL = [opt[3] for opt in CL_OPTS]



__all__ = ['usage', 'OPTIONS', 'SHORT', 'LONG',
           'GETOPT_SHORT', 'GETOPT_LONG', 'CL']
