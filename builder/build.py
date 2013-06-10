# -*- coding: utf-8 -*-

from builder.oset import OrderedSet
from builder.functions import print_array
from builder.package import Package
from builder.utils import print_graph
from builder import settings, config
import logging
import subprocess
import os
import sys


def get_build_instructions(package_list, origin_package_set):
    # Place packages according to it's action types
    packages = {}
    norebuild = getattr(settings, 'NO_REBUILD_INSTALLED', False)
    for package in package_list:
        action = package.action(origin_package_set)
        if action not in packages:
            packages[action] = []
        packages[action].append(package)
        # Add package to build order if it must be rebuilt
        if action == 'install' and not norebuild:
            if 'build' not in packages:
                packages['build'] = []
            packages['build'].append(package)

    for key in ('install', 'keep', 'missing'):
        if key in packages:
            packages[key] = list(OrderedSet(packages[key]))

    return packages



def print_instructions(packages):
    for key in packages:
        logging.info("%s:", key.upper())
        print_array(packages[key], logging.info)
    logging.info("-" * 10)


def install_packages(install):
    if not install:
        return
    subprocess.check_call(['mpkg-install -y {0}'.format(
            ' '.join(map(lambda x: x.name, install)))], shell=True)


def build_packages(build):
    counter = 0
    total = len(build) + 1

    logging.info("Build started.")
    skip = int(config.getopt('start_from', 0))
    skip_failed = getattr(settings, 'SKIP_FAILED', False)
    mkpkg_opts = '' if getattr(settings, 'NO_INSTALL') else '-si'

    for package in build:
        counter += 1
        if counter <= skip:
            continue
        s = "[{0}/{1}] {2}: building...".format(counter, total, package)
        sys.stdout.write("\x1b]2;{0}\x07".format(s))
        sys.stdout.flush()
        logging.info(s)

        path = os.path.join(settings.ABUILD_PATH, package.name)
        if subprocess.call("cd {0} && mkpkg {1}".format(path, mkpkg_opts), shell=True):
            logging.info("BUILD FAILED")
            if not skip_failed:
                logging.error("%s failed to build, stopping.", package)
                logging.info("Successfully built: %s of %s packages.", counter-1, total)
                return
        else:
            logging.info("BUILD OK")


def process_list(package_list, origin_package_set):
    packages = get_build_instructions(package_list, origin_package_set)
    print_instructions(packages)

    # Check for missing packages
    if 'missing' in packages:
        if not getattr(settings, 'IGNORE_MISSING', False):
            logging.error("Errors detected: packages missing: %s",
                ' '.join(map(lambda x: x.name, packages['missing'])))
            return

    # Create graph if requested
    graph = config.getopt('graph_path', None)
    if graph:
        highlight = config.getopt('highlight_graph', '')
        highlight = [Package(p) for p in highlight.split()]
        print_graph(package_list, graph, highlight)
        return

    install_packages(packages.get('install', []))
    build_packages(packages.get('build', []))
