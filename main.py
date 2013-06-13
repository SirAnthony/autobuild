#!/usr/bin/env python
# -*- coding: utf-8 -*-

from builder import config
from builder.buildorder import get_build_order
from builder.build import process_list
from builder.pset import PackageSet
from builder.utils import gettext as _
import logging
import sys


if __name__ == '__main__':
    logging.info(_("Loading abuilds, this can take a time..."))
    package_set = PackageSet(config.package_list)
    build_order = get_build_order(package_set)
    process_list(build_order, package_set)
    sys.exit(0)
