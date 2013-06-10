# -*- coding: utf-8 -*-

from builder.utils import popen
from builder.path import guess_path
import os


_default_path = ""

ABUILD_VARS = ['pkgname', 'pkgver', 'pkgbuild', 'build_deps']

class Abuild(object):

    def __init__(self, path):
        self.path = path
        for item in ABUILD_VARS:
            data, error = popen("./get_abuild_var.sh", "build_deps", abuild)
            setattr(self, item, data)
        self.build_deps = self.build_deps.split()


def path(pkgname):
    if not _default_path:
        _default_path = guess_path(settings.ABUILD_PATH)
    return os.path.join(_default_path.localpath, pkgname, 'ABUILD')
