# -*- coding: utf-8 -*-

"""PackageSet class"""
from .package import Package
from .mset import MergableSet


class PackageSet(MergableSet):

    def __init__(self, package_list=set()):
        # Do merge
        package_list = map(lambda name: \
            Package(name) if isinstance(name, basestring) \
            else name, package_list)
        super(PackageSet, self).__init__(package_list)

    def get_dep_tree(self):
        """Recursively get all dependencides of packages in set."""
        if not len(self):
            return []
        unprocessed = set(self)
        processed = PackageSet()
        while unprocessed:
            for package in list(unprocessed):
                unprocessed |= package.deps - processed
                processed.add(package)
                unprocessed.remove(package)
        return processed

    def merge(self):
        super(PackageSet, self).merge(
            lambda p: p.abuild and p.name != p.abuild.pkgname,
            lambda p: Package(p.abuild.pkgname, claimer=p))
