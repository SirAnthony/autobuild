#!/usr/bin/env python
# -*- coding: utf-8 -*-

from agibuild import config
from agibuild import settings
from agibuild.buildorder import get_build_order
from agibuild.build import process_list
from agibuild.pset import PackageSet, get_installed
from agibuild.options import usage
from agibuild.output import info as _
import logging
import sys


if __name__ == '__main__':
    _("{c.yellow}Loading abuilds, this can take a time...")
    package_set = PackageSet(config.package_list)
    if not package_set and config.clopt('update'):
        package_set = get_installed().updates()
    if not package_set:
        usage(settings.PROG_NAME)
    build_order = get_build_order(package_set)
    process_list(build_order, package_set)
    sys.exit(0)