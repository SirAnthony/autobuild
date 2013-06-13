# -*- coding: utf-8 -*-

from builder.functions import print_array
from builder.pset import PackageSet
from builder.resolver import Resolver
from builder.utils import gettext as _
import logging


def get_build_order(package_set):
    logging.info(_("Merging requested packages..."))
    package_set.merge()
    deps = package_set.get_dep_tree()
    logging.info(_("Merging subpackages..."))
    # Always merge multipackages. From now, this is mandatory.
    deps = PackageSet(deps).merge_multi_packages()
    logging.info(_("Calculating deps..."))
    build_order = Resolver(deps)
    #import pudb; pudb.set_trace()
    return build_order.resolve()
