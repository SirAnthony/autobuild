# -*- coding: utf-8 -*-

import cStringIO
import traceback
import subprocess
from . import config
from .output import ( info as _,
                      debug as _d,
                      error as _e )



def excepthook(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.

    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """
    notice = \
        """{c.red}An unhandled exception occurred. Please report the problem\n"""\
        """{c.red}Error information:{c.end}\n"""

    tbinfofile = cStringIO.StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = u'{0}: \n{1}'.format(excType, excValue)
    msg = u'\n'.join([notice, errmsg, tbinfo])
    _e(msg)



def popen(*args):
    process = subprocess.Popen(args,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.communicate()


def print_graph(packages, fname, highlight=[]):
    data = ["digraph G {"]
    data.extend(['\t"{0}" [fontcolor = red, color = red];'.format(p.name) \
            for p in highlight])
    for package in packages:
        data.extend(['\t"{1}" -> "{0}";'.format(d.name, package.name) \
                        for d in package.deps])
    data.append("}")
    data = '\n'.join(data)
    with open('{0}.dot'.format(fname), 'w') as f:
        f.write(data)
    try:
        if subprocess.call(["dot -Tpng -O {0}.dot".format(fname)]):
            _("""{c.green}File created but was not plotted."""\
              """Plot it with {c.white}dot -O{0}.dot""", fname)
        else:
            _("{c.green}Graph was plotted at {c.magnetta}{0}.png", fname)
    except OSError:
        pass
    return



def print_array(array, log_callback):
    """Prints array elements (used for output results)"""
    if not array:
        _d('ZERO-LENGTH ARRAY')
        return
    numerate = config.clopt('numerate')

    array = ["{0}{1}".format(
        '[{0}] '.format(number) if numerate else '', item) \
            for number, item in enumerate(array)]
    log_callback('\n'.join(array))



def unique(seq, idfun=None):
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result
