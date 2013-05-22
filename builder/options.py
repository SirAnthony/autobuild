
import logging

"""Options module
This module holds all options program have
Options format:
    (short_name, long_name, description, arguments_count, return_name, processing_callback)

Callback function may be anything, but if it returns False
program execution stops after call of this functuin
"""

class StopExecution(Exception):
    pass


def opt_help(prog_name, *args, **kwargs):
    print """\
Usage:  [{0}] filename
        [{0}] package1, package2, package3, ...

""".format(''.join([x[0] for x in OPTIONS]))
    for item in OPTIONS:
        print "\t-{0} --{1}\t\t{2}".format(*item)
    raise StopExecution


OPTIONS = (
    ('h', 'help', 'Show this help message and exit', None, 0, opt_help),
    ('t', 'abuilds-tree', 'Specify path to directory with abuilds',
        'abuild_path', 1, None),
)

SHORT_OPTIONS = dict([('-{0}'.format(x[0]), x[-3:]) for x in OPTIONS])
LONG_OPTIONS = dict([('--{0}'.format(x[1]), x[-3:]) for x in OPTIONS])

def opt(name, mod, char):
    return '{0}{1}'.format(name, '' if not mod else char)

def short_opts():
    return ''.join([opt(x[0], x[-2], ':') for x in OPTIONS])

def long_opts():
    return [opt(x[1], x[-2], '=') for x in OPTIONS]
