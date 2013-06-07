# -*- coding: utf-8 -*-

from builder.path import guess_path
import os


_default_path = ""



def path(pkgname):
    if not _default_path:
        _default_path = guess_path(settings.ABUILD_PATH)
    return os.path.join(_default_path.localpath, pkgname, 'ABUILD')
