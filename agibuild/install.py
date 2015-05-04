# -*- coding: utf-8 -*-

from . import settings, config
from .package import PKG_STATUS_STR
from .output import ( info as _,
                      warn as _w,
                      error as _e )
import subprocess

PACKAGES_INSTALLED = []

def build():
    return settings.opt('rebuild_installed') \
        and not settings.opt('no_install')

def from_list(packages, origin):
    if not packages or settings.opt('no_install'):
        return
    def need_install(package):
        return package.action(origin) == PKG_STATUS_STR.install
    install = filter(need_install, packages)
    if not install:
        return
    PACKAGES_INSTALLED.extend(install)
    subprocess.check_call(['mpkg-install {0}'.format(
        ' '.join(map(lambda x: x.name, install)))], shell=True)

def remove_installed():
    if not config.clopt('accurate'):
        _w('{c.yellow}Packages can be removed only in accurate mode')
        return
    subprocess.check_call(['mpkg-remove {0}'.format(
        ' '.join(map(lambda x: x.name, PACKAGES_INSTALLED)))], shell=True)

__all__ = ['needed', 'from_list', 'remove_installed']

