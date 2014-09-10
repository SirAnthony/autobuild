# -*- coding: utf-8 -*-

from . import settings
from .path import guess_path
from .utils import popen
from .output import (info as _, debug as _d, error as _e)

import json
import os


DEFAULT_PATH = ""

MANDATORY_VARS = ['pkgname', 'pkgver', 'pkgbuild']
OPTIONAL_VARS = ['build_deps', 'adddep', 'provides', 'conflicts']
ABUILD_VARS = MANDATORY_VARS + OPTIONAL_VARS


VER_OPS = {
    '==': '__eq__',
    '=': '__eq__',
    '>=': '__gte__',
    '<=': '__lte__',
    '>': '__gt__',
    '<': '__lt__',
    '!=': '__ne__'
}


class AbuildError(Exception):
    pass


class AbuildMeta(type):
    _cache = {}

    def __call__(cls, pkgname, *args, **kwargs):
        """Create only core abuilds"""
        abuild_dir = get_path(pkgname)
        path = os.path.join(abuild_dir, 'ABUILD')
        if not os.path.exists(path):
            _d("{c.red}GET_ERROR: No such file {c.white}{c.bold}{0}", path)
            return None

        if path in cls._cache:
            return cls._cache[path]

        script = os.path.join(settings.SCRIPT_PATH, "get_corepackage.sh")
        data, error = popen(script, path)
        name = ''.join(data.strip().splitlines()) or pkgname
        if name != pkgname:
            return Abuild(name)

        cls._cache[path] = abuild = super(AbuildMeta, cls).__call__(
            name, path, abuild_dir, *args, **kwargs)
        return abuild


class Abuild(object):
    __metaclass__ = AbuildMeta

    def __init__(self, name, abuild, abuild_dir):
        self.path = abuild
        self.location = abuild_dir
        script = os.path.join(settings.SCRIPT_PATH, "get_abuild_var.sh")
        data, error = popen(script, abuild, *ABUILD_VARS)
        if error:
            raise _e(u"{c.red}Error in abuild {c.yellow}{0}{c.red}:\n{1}",
                     AbuildError, name, error.decode("utf-8"))
        data = json.loads(data)
        for key, value in data.items():
            if key not in ABUILD_VARS:
                raise _e("{c.red}Unexpected key {c.cyan}{0}{c.red} in \
ABUILD {c.yellow}{1}{c.red}. Probably script error.", AbuildError, key, name)
            if not value and key in MANDATORY_VARS:
                raise _e("{c.red}Variable {c.cyan}{0}{c.red} not found \
in ABUILD {c.yellow}{1}", AbuildError, key, name)

            setattr(self, key, value)
        self.parse_deps()

    def pkg_list(pkgname):
        return self.pkglist.split()

    def parse_deps(self):
        def _parse(pkgname):
            name, op, ver = pkgname, '', ''
            for vop in VER_OPS.keys():
                if pkgname.find(vop) >= 0:
                    op, (name, ver) = vop, pkgname.split(vop)
                    break
            return (name, (op, ver))

        deps = self.build_deps.split()
        self.build_deps_verbose = deps = dict([_parse(x) for x in deps])
        self.build_deps = deps.keys()

        adeps = self.adddep.split()
        self.adddep_verbose = adeps = dict([_parse(x) for x in adeps])
        self.adddep = adeps.keys()


def get_path(pkgname):
    global DEFAULT_PATH
    if not DEFAULT_PATH:
        DEFAULT_PATH = guess_path(settings.ABUILD_PATH)
    return os.path.join(DEFAULT_PATH.localpath, pkgname)


__all__ = ['Abuild', 'AbuildError', 'DEFAULT_PATH']
