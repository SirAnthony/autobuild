# -*- coding: utf-8 -*-

import cStringIO
import logging
import traceback
import subprocess


def excepthook(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.

    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """
    notice = \
        """An unhandled exception occurred. Please report the problem\n"""\
        """Error information:\n"""

    tbinfofile = cStringIO.StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = u'{0}: \n{1}'.format(excType, excValue)
    msg = u'\n'.join([errmsg, tbinfo])
    logging.error(msg)


def popen(*args):
    process = subprocess.Popen(args,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.communicate()

def gettext(text):
    """Localisation hook"""
    return unicode(text)


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
        if subprocess.call(["dot", "-Tpng", "-O {0}.dot".format(fname)]):
            logging.debug("File created but was not plotted. Plot it with \
`dot -O{0}.dot".format(fname))
        else:
            logging.debug("Graph was plotted at {0}.png".format(fname))
    except OSError:
        pass
    return


class AttrDict(dict):

    def __init__(self, indict=None):
        if indict is None:
            indict = {}
        dict.__init__(self, indict)

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            c = AttrDict()
            self.__setattr__(item, c)
            return c

    def __setattr__(self, item, value):
        if self.__dict__.has_key(item):
            dict.__setattr__(self, item, value)
        else:
            if isinstance(value, dict):
                self.__setitem__(item, AttrDict(value))
            else:
                self.__setitem__(item, value)
