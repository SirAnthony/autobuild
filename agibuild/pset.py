# -*- coding: utf-8 -*-

"""PackageSet class"""
from . import settings
from .package import Package, mpkg_db
from .mset import MergableSet
from .output import error as _e


class PackageSet(MergableSet):

    def __init__(self, package_list=set()):
        # Do merge
        package_list = map(lambda name: \
            Package(name) if isinstance(name, basestring) \
            else name, package_list)
        super(PackageSet, self).__init__(package_list)

    def extend_with_deps(self):
        for package in list(self):
            self.update(package.dependants)

    def get_dep_tree(self):
        """Recursively get all dependencides of packages in set."""
        if not len(self):
            return []
        unprocessed = set(self)
        processed = PackageSet()
        adddep = not settings.opt('no_install')
        while unprocessed:
            for package in list(unprocessed):
                unprocessed |= package.deps - processed
                if adddep:
                    unprocessed |= package.installdeps - processed
                processed.add(package)
                unprocessed.remove(package)
        return processed

    def merge(self):
        super(PackageSet, self).merge(
            lambda p: p.abuild and p.name != p.abuild.pkgname,
            lambda p: Package(p.abuild.pkgname, claimer=p))

    def updates(self):
        """Returns new package set with packages from current that
           must be updated"""
        return PackageSet(filter(lambda x: x.updatable, self))

    @staticmethod
    def installed():
        """Returns new package set with currently installed packages."""
        stat, data = mpkg_db.getRecords('packages', ['package_name'],
                        package_installed=1)
        if not stat:
            raise _e("{c.red}Unexpected result while fetching db: {0}",
                       ValueError, data)
        return PackageSet(sum(data, ()))

