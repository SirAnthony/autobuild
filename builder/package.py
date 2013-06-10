# -*- coding: utf-8 -*-

from builder import settings
from builder.abuild import Abuild, AbuildError
from builder.skyfront import SkyFront
from builder.utils import gettext as _
import os.path
import logging

mpkg_db = SkyFront('sqlite', '/var/mpkg/packages.db')


class Package(object):

    _cache = []

    def __new__(cls, name):
        """Create only one instance per package"""
        if not name:
            import pudb; pudb.set_trace()
        for package in cls._cache:
            if package.name == name:
                return package
        package = super(Package, cls).__new__(cls)
        cls._cache.append(package)
        return package


    def __init__(self, name):
        self.name = name
        self._twice = False
        self.priority = 0
        self.in_loop = []

    def __str__(self):
        return "Package {0}".format(self.name)
    def __unicode__(self):
        return unicode(self.__str__())
    def __repr__(self):
        return self.__unicode__()


    def _get_abuild(self):
        if not hasattr(self, '_abuild'):
            self._abuild = Abuild(self.name)
            if not self._abuild:
                raise AbuildError(_("""Abuild for {0} not found of contains errors.
Build stopped.""").format(self.name))

        return self._abuild
    abuild = property(_get_abuild)


    def _get_deps(self):
        if not hasattr(self, '_deps'):
            self._deps = set(map(lambda p: Package(p),
                    filter(lambda n: n and n not in settings.BLACKLIST_PACKAGES,
                    self.abuild.build_deps)))
            if self in self._deps:
                self._deps.remove(self)
                self._twice = True
        return self._deps
    deps = property(_get_deps)


    def _is_installed(self):
        if not hasattr(self, '_installed'):
            stat, data = mpkg_db.getRecords('packages',
                        ['package_version', 'package_build'], limit=1,
                        package_name=self.name, package_installed=1)
            self._installed = bool(len(data))
        return self._installed
    installed = property(_is_installed)


    def _is_avaliable(self):
        if not hasattr(self, '_avaliable'):
            stat, data = mpkg_db.getRecords('packages',
                            ['package_version', 'package_build'],
                            limit=1, package_name=self.name)
            self._avaliable = bool(len(data))
        return self._avaliable
    avaliable = property(_is_avaliable)


    def _is_abuild_exist(self):
        return bool(self.abuild)
    abuild_exist = property(_is_abuild_exist)


    # Temporarily, assume that any package can be built
    can_be_build = True


    def enqueue(self, build_order):
        """Check if all deps in build_order"""
        diff = set(self.deps) - set(build_order)
        if not diff:
            logging.debug(_("ALL DEPS OK: Adding %s\n"), self.name)
            return True
        logging.debug(_("DEP FAIL: %s => %s"), self.name,
                ', '.join([d.name for d in diff]))
        return False


    def action(self, force):
        if self in force:
            if self.abuild_exist and self.can_be_build:
                return 'build'
        elif self.installed:
            return 'keep'
        elif self.avaliable:
            return 'install'
        elif self.abuild_exist and self.can_be_build:
            return 'build'
        return 'missing'
