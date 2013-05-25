#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Load logging system
from builder import config
from builder import settings
from builder.buildorder import get_build_order
from builder.build import process_list
from builder.pset import PackageSet
from builder.functions import print_array
import sys
import logging


if __name__ == '__main__':
    package_set = PackageSet(config.package_list)
    build_order = get_build_order(package_set)
    if getattr(settings, 'LIST_ORDER', False):
        print_array(map(lambda x: x.name, build_order), logging.info)
    else:
        process_list(build_order, package_set)

    sys.exit(0)
