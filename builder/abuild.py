# -*- coding: utf-8 -*-

from builder.path import guess_path
from builder.utils import popen, force_unicode
from builder import settings
from builder.utils import gettext as _
import logging
import os


DEFAULT_PATH = ""

MANDATORY_VARS = ['pkgname', 'pkgver', 'pkgbuild']
OPTIONAL_VARS = ['build_deps']
ABUILD_VARS = MANDATORY_VARS + OPTIONAL_VARS


VER_OPS = {
  '==': '__eq__',
  '>=': '__gte__',
  '<=': '__lte__',
  '>': '__gt__',
  '<': '__lt__',
  '!=': '__ne__'
}


class AbuildError(Exception):
    pass


class Abuild(object):

    def __new__(cls, pkgname):
        """Create only core abuilds"""
        path = get_path(pkgname)
        if not os.path.exists(path):
            logging.debug("GET_ERROR: No such file %s", path)
            return None
        data, error = popen("./get_corepackage.sh", path)
        name = ''.join(data.strip().splitlines()) or pkgname
        return super(Abuild, cls).__new__(cls)


    def __init__(self, name):
        self.path = abuild = get_path(name)
        for item in ABUILD_VARS:
            data, error = popen("./get_abuild_var.sh", item, abuild)
            if error:
                text = _(u"Error in abuild {0}:\n{1}").format(name, error.decode("utf-8"))
                logging.error(text)
                raise AbuildError(text)
            data = ' '.join(data.splitlines()).strip()
            if not data and item in MANDATORY_VARS:
                raise AbuildError(_("Variable {0} not found in ABUILD {1}").format(item ,name))
            setattr(self, item, data)
        self.parse_deps()

    def parse_deps(self):
        def _parse(pkgname):
            name, op, ver = pkgname, '', ''
            for vop in VER_OPS.keys():
                if pkgname.find(vop) >= 0:
                    op, (name, ver) = vop, pkgname.split(vop)
                    break
            return (name, (op, ver))

        deps = self.build_deps.split()
        self.build_deps_verbose = deps = dict(
                    [_parse(x) for x in deps])
        self.build_deps = deps.keys()


def get_path(pkgname):
    global DEFAULT_PATH
    if not DEFAULT_PATH:
        DEFAULT_PATH = guess_path(settings.ABUILD_PATH)
    return os.path.join(DEFAULT_PATH.localpath, pkgname, 'ABUILD')



__all__ = ['Abuild', 'AbuildError', 'DEFAULT_PATH']
