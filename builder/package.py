# -*- coding: utf-8 -*-

from builder import settings
from builder.abuild import Abuild, AbuildError
from builder.mset import MergableSet
from builder.skyfront import SkyFront
from builder.utils import AttrDict, popen, gettext as _
from builder import config
import os.path
import logging

PKG_STATUS_NAMES = ('install', 'build', 'missing', 'keep')
PKG_STATUS = AttrDict([(name, n) for n, name in enumerate(PKG_STATUS_NAMES)])
PKG_STATUS_STR = AttrDict([(name, name) for name in PKG_STATUS_NAMES])




mpkg_db = SkyFront('sqlite', '/var/mpkg/packages.db')


class PackageMeta(type):

    _cache = {}
    _provides = {}

    def __call__(cls, name, *args, **kwargs):
        """Create only one instance per package"""
        if name in cls._cache:
            return cls._cache[name]
        # No alternatives
        if name in cls._provides:
            return cls._provides[name]

        package = super(PackageMeta, cls).__call__(name, *args, **kwargs)
        cls._cache[name] = package
        return package


class Package(object):
    __metaclass__ = PackageMeta

    def __init__(self, name):
        #if getattr(self, "_init", False):
        #    return
        self._init = True
        self.name = name
        self._twice = False
        self.priority = 0
        self.in_loop = []
        self.dep_for = set()

    def __str__(self):
        return "Package {0}".format(self.name)
    def __unicode__(self):
        return unicode(self.__str__())
    def __repr__(self):
        return self.__unicode__()


    @property
    def abuild(self):
        if not hasattr(self, '_abuild'):
            self._abuild = abuild = Abuild(self.name)
            if not abuild:
                logging.error(_("Abuild for %s not found of contains errors."), self.name)
            elif abuild.provides:
                self.__metaclass__._provides[abuild.provides] = self
        return self._abuild

    @property
    def base(self):
        if self.abuild and self.abuild.pkgname != self.name:
            return Package(self.abuild.pkgname)
        return self

    @property
    def deps(self):
        if not self.abuild_exist:
            return frozenset()
        if not hasattr(self, '_deps'):
            self._deps = MergableSet(map(lambda p: Package(p),
                filter(lambda n: n and n not in settings.BLACKLIST_PACKAGES,
                self.abuild.build_deps)))
            self._deps.merge(lambda p: p.abuild and p.name != p.abuild.pkgname,
                             lambda p: Package(p.abuild.pkgname))
            if self in self._deps:
                self._deps.remove(self)
                self._twice = True
            for dep in self._deps:
                dep.dep_for.add(self)
        return self._deps

    @property
    def installed(self):
        if not hasattr(self, '_installed'):
            stat, data = mpkg_db.getRecords('packages',
                        ['package_version', 'package_build'], limit=1,
                        package_name=self.name, package_installed=1)
            self._installed = data[0] if data else ()
        return self._installed

    @property
    def avaliable(self):
        if not hasattr(self, '_avaliable'):
            stat, data = mpkg_db.getRecords('packages',
                            ['package_version', 'package_build'],
                            limit=1, package_name=self.name)
            self._avaliable = data[0] if data else ()
        return self._avaliable


    @property
    def abuild_exist(self):
        return bool(self.abuild)

    @property
    def buildable(self):
        return self.abuild_exist


    def enqueue(self, build_order):
        """Check if all deps in build_order"""
        diff = set(self.deps) - set(build_order)
        if not diff:
            logging.debug(_("ALL DEPS OK: Adding %s\n"), self.name)
            return True
        logging.debug(_("DEP FAIL: %s => %s"), self.name,
                ', '.join([d.name for d in diff]))
        return False


    def vercmp(self, version, build):
        """Compare version by using of mpkg"""
        if not self.abuild:
            return 1
        result, error = popen('mpkg-vercmp', self.abuild.pkgver, version)
        if error:
            raise OSError(error)
        if int(result) is 0:
            result = cmp(self.abuild.pkgbuild, build)
        return int(result)


    def action(self, force):
        if self in force:
            if self.buildable:
                return PKG_STATUS_STR.build
        elif self.installed:
            if config.clopt('update') and self.vercmp(*self.installed) > 0:
                return PKG_STATUS_STR.build
            return PKG_STATUS_STR.keep
        elif self.avaliable:
            return PKG_STATUS_STR.install
        elif self.buildable:
            return PKG_STATUS_STR.build
        return PKG_STATUS_STR.missing
