# -*- coding: utf-8 -*-

from builder.oset import OrderedSet
from builder.functions import print_array
from builder.package import Package, PKG_STATUS_STR, PKG_STATUS_NAMES
from builder.utils import print_graph, AttrDict
from builder import settings, config
from math import log10, ceil
import logging
import subprocess
import os
import sys


COLORS = AttrDict(settings.COLORS)
NO_COLORS = AttrDict([(key, '') for key in COLORS.keys()])

def get_colors():
    return COLORS if getattr(settings, 'COLORIZE', False) else NO_COLORS

def package_depens(pkg, status, colors):
    if not pkg.dep_for or (status != PKG_STATUS_STR.missing and \
        not getattr(settings, 'PRINT_DEPENDS', False)):
        return ''
    return ' <= {c.miss_dep}{0}{c.end}'.format(
            ' '.join([p.name for p in pkg.dep_for]), c=colors)

def package_version(pkg, status, colors):
    if status == PKG_STATUS_STR.missing:
        return ''
    elif status == PKG_STATUS_STR.install:
        return '[{0}-{1}]'.format(*pkg.avaliable)
    elif status == PKG_STATUS_STR.keep:
        return '[{0}-{1}]'.format(*pkg.installed)
    string = ''
    if pkg.installed:
        string = '{0}-{1} -> '.format(*pkg.installed)
    return '{c.old_version}{0}{c.version}{1}-{2}'.format(string,
        pkg.abuild.pkgver, pkg.abuild.pkgbuild, c=colors)


def print_instructions(packages):
    colors = get_colors()

    for key in PKG_STATUS_NAMES:
        if key not in packages:
            continue

        string = []
        string.append("{c.title}Packages for action {c.bold}{0}{c.end}:".format(
                    key.upper(), c=colors))
        signs = int(ceil(log10(len(packages[key]))))
        for n, package in enumerate(packages[key]):
            number = '{0:>{1}}: '.format(n, signs) if config.clopt('numerate') else ''
            depends = package_depens(package, key, colors)
            version = package_version(package, key, colors)
            string.append("{c.title}{3}{c.end}{color}{0.name} {c.version}{1}{c.end}{2}".format(
              package, version, depends, number, c=colors, color=colors[key]))
        logging.info('\n'.join(string))
    total = 0
    totalstr = ''
    for k, v in packages.items():
        total += len(v)
        totalstr += "{0}: {c.bold}{1}{c.end} ".format(k.capitalize(), len(v), c=colors)
    logging.info('Total: {c.version}{c.bold}{0}{c.end} {1}'.format(
            total, totalstr, c=colors))


def get_build_instructions(package_list, origin_package_set):
    # Place packages according to it's action types
    packages = {}
    norebuild = getattr(settings, 'NO_REBUILD_INSTALLED', False)
    build_keep = config.clopt('build_keep')
    for package in package_list:
        action = package.action(origin_package_set)
        if action not in packages:
            packages[action] = []
        packages[action].append(package)
        # Add package to build order if it must be rebuilt
        rebuild = ((action == PKG_STATUS_STR.install and not norebuild)
                or (action == PKG_STATUS_STR.keep and build_keep ))
        if rebuild:
            if package.buildable:
                build_name = PKG_STATUS_STR.build
            else:
                build_name = PKG_STATUS_STR.missing
            if build_name not in packages:
                packages[build_name] = []
            packages[build_name].append(package)

    for key in (PKG_STATUS_STR.install, PKG_STATUS_STR.keep, PKG_STATUS_STR.missing):
        if key in packages:
            packages[key] = list(OrderedSet(packages[key]))

    return packages

def install_packages(install):
    if not install:
        return
    subprocess.check_call(['mpkg-install -y {0}'.format(
            ' '.join(map(lambda x: x.name, install)))], shell=True)


def build_packages(build):
    counter = 0
    colors = get_colors()
    total = len(build) + 1

    logging.info("Build started.")
    skip = int(config.clopt('start_from', 0))
    skip_failed = getattr(settings, 'SKIP_FAILED', False)
    mkpkg_opts = '' if getattr(settings, 'NO_INSTALL', False) else '-si'

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
    colors = get_colors()

    no_deps = [p.name for p in package_list if not p.deps]
    if no_deps and config.clopt('with_deps', False):
        logging.info("{c.title}Packages without build_deps:{c.end} {c.version}{0}{c.end}".format(
                        ' '.join(no_deps), c=colors))
        return

    # Only print
    if config.clopt('list_order'):
        return

    # Check for missing packages
    if 'missing' in packages:
        if not getattr(settings, 'IGNORE_MISSING', False):
            logging.error("Errors detected: packages missing: %s",
                ' '.join(map(lambda x: x.name, packages[PKG_STATUS_STR.missing])))
            return

    # Create graph if requested
    graph = config.clopt('graph_path', None)
    if graph:
        highlight = config.clopt('highlight_graph', '')
        highlight = [Package(p) for p in highlight.split()]
        print_graph(package_list, graph, highlight)
        return

    if getattr(settings, 'ASK', False):
        logging.info('{c.bold}{c.title}Are you {c.build}ready to build{c.title} packages?\
 [{c.build}Y{c.title}/{c.missing}n{c.title}]{c.end}'.format(c=colors))
        answer = ''.join(sys.stdin.read(1).splitlines())
        if answer not in ('', 'y', 'Y'):
            return

    install_packages(packages.get(PKG_STATUS_STR.install, []))
    build_packages(packages.get(PKG_STATUS_STR.build, []))
