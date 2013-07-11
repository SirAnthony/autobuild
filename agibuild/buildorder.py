# -*- coding: utf-8 -*-

from . import config
from .package import Package
from .pset import PackageSet
from .resolver import Resolver
from .output import info as _


def get_build_order(package_set):
    _("{c.green}Loading alternatives...")
    Package.fetch_provides()
    _("{c.green}Merging requested packages...")
    package_set.merge()
    Package.fetch_versions()
    if config.clopt('build_deps'):
        _("{c.green}Fetching dependencies...")
        Package.fetch_dependencies()
        package_set.extend_with_deps()
    _("{c.green}Building tree...")
    deps = package_set.get_dep_tree()
    _("{c.green}Merging subpackages...")
    # Always merge multipackages. From now, this is mandatory.
    deps = PackageSet(deps).merge_multi_packages()
    _("{c.green}Fetching versions...")
    _("{c.green}Calculating deps...")
    build_order = Resolver(deps)
    return build_order.resolve()
