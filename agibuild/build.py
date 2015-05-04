# -*- coding: utf-8 -*-

from . import settings, config
from . import install
from .oset import OrderedSet
from .adict import AttrDict
from .package import Package, PKG_STATUS_STR, PKG_STATUS_NAMES
from .utils import print_graph, print_array
from .output import ( info as _,
                      warn as _w,
                      error as _e )

from math import log10, ceil
import subprocess
import os
import sys
import time


def print_instructions(packages):
    print_keep = config.clopt('build_keep') or config.clopt('show_keep')
    for key in PKG_STATUS_NAMES:
        if key not in packages:
            continue

        if key == PKG_STATUS_STR.keep and not print_keep:
            continue

        string = []
        string.append("{c.white}Packages for action {c.bold}{0}{c.end}:")
        signs = int(ceil(log10(len(packages[key]))))
        for n, package in enumerate(packages[key], 1):
            number = '{0:>{1}}: '.format(n, signs) if config.clopt('numerate') else ''
            string.append("{c.white}" + number + "{c.end}{c." + key + "}" +
                            package.output(key))
        _('\n'.join(string), key.upper())

    total = 0
    totalstr = []
    for k, v in packages.items():
        total += len(v)
        totalstr.extend([k.capitalize(), ": {c.bold}", str(len(v)), "{c.end} "])
    _("Total: {c.version}{c.bold}{0}{c.end} " + ''.join(totalstr), total)


def get_build_instructions(package_list, origin_package_set):
    # Place packages according to it's action types
    packages = {}
    rebuild_installed = settings.opt('rebuild_installed')
    build_keep = config.clopt('build_keep')
    for package in package_list:
        action = package.action(origin_package_set)
        if action not in packages:
            packages[action] = []
        packages[action].append(package)
        if action == PKG_STATUS_STR.install and not rebuild_installed:
            _e("""{c.red}Internal error: package {c.yellow}{0}{c.red}"""\
               """ must not be installed in build phase. Exiting.""")
            return
        # Add package to build order if it must be rebuilt
        rebuild = ((action == PKG_STATUS_STR.install and rebuild_installed)
                or (action == PKG_STATUS_STR.keep and build_keep))
        if rebuild:
            if package.buildable:
                build_name = PKG_STATUS_STR.build
            else:
                build_name = PKG_STATUS_STR.missing
            if build_name not in packages:
                packages[build_name] = []
            packages[build_name].append(package)

    for key in (PKG_STATUS_STR.keep, PKG_STATUS_STR.missing):
        if key in packages:
            packages[key] = list(OrderedSet(packages[key]))

    return packages


def build_packages(build):
    total = len(build)

    _("{c.bold}{c.green}Build started.")
    skip = int(config.clopt('start_from', 0))
    skip_failed = settings.opt('skip_failed')
    mkpkg_opts = '' if settings.opt('no_install') else '-si'
    outfile = config.clopt("output_file")
    status = []

    logdir = os.path.join(settings.LOG_PATH, "build", "{0:d}".format(time.time()))
    os.mkdir(logdir)
    for counter, package in enumerate(build):
        if counter < skip:
            continue
        state_item = {}
        s = "[{0}/{1}] {2}: building...".format(counter+1, total, package)
        logfile = os.path.join(logdir, "{0}{1:d}.log".format(package.name, time.time()))
        output_method =  ">" if outfile else "| tee"
        if sys.stdout.isatty():
            sys.stdout.write("\x1b]2;{0}\x07".format(s))
            sys.stdout.flush()
        _("{c.green}" + s)
        if config.clopt('accurate'):
            _("{c.green} installing dependencies")
            install.from_list(package.deps)
            install.from_list(package.installdeps)
            # TODO: log installed packages to status

        path = package.abuild.location
        command = "cd {0} && mkpkg {1} {2} {3} 2>&1".format(path, mkpkg_opts,
                output_method, logfile)
        ext_code = subprocess.call(command, shell=True)
        status.append({"code": ext_code, "output": logfile, "success": bool(not ext_code)})
        if ext_code:
            _w("{c.red}BUILD FAILED")
            if not skip_failed:
                _e("{c.red}Package {c.cyan}{0}{c.red} failed to build, stopping.", None, package.name)
                _("""{c.white}Successfully built: {c.bold}{c.yellow}{0}{c.white}{c.end}"""\
                  """ of {c.bold}{c.yellow}{1}{c.white}{c.end} packages.""", counter, total)
                break
        else:
            _("{c.green}BUILD OK")

    if outfile:
        with open(outfile, 'w') as ofile:
            json.dump(status, o)


def process_list(package_list, origin_package_set):
    packages = get_build_instructions(package_list, origin_package_set)
    if packages is None:
        return

    print_instructions(packages)

    no_deps = [p.name for p in package_list if not p.deps]
    if no_deps and config.clopt('with_deps', False):
        _w("{c.white}Packages without build_deps:{c.end} {c.yellow}{0}",
                ' '.join(no_deps))
        return

    # Only print
    if config.clopt('list_order'):
        return

    # Check for missing packages
    if 'missing' in packages and not settings.opt('ignore_missing'):
        missing = map(lambda x: x.name, packages[PKG_STATUS_STR.missing])
        _e("{c.red}Errors detected: packages missing: {c.cyan}{0}",
            None, ' '.join(missing))
        return

    # Create graph if requested
    graph = config.clopt('graph_path', None)
    if graph:
        highlight = config.clopt('highlight_graph', '')
        highlight = [Package(p) for p in highlight.split()]
        print_graph(package_list, graph, highlight)
        return

    skip = int(config.clopt('start_from', 0))
    build_order = packages.get(PKG_STATUS_STR.build, [])
    if skip and skip < len(build_order):
        _("{c.white}Build will be started from {c.bold}{c.yellow}{0}{c.end}",
            build_order[skip].name)

    if settings.opt('ask'):
        _("""{c.bold}{c.white}Are you {c.green}ready to build{c.white}"""\
          """ packages? [{c.green}Y{c.white}/{c.red}n{c.white}]{c.end}""")
        answer = ''.join(sys.stdin.read(1).splitlines())
        if answer not in ('', 'y', 'Y'):
            return
    if not config.clopt('accurate'):
        install.process(packages)
    build_packages(build_order)
    if config.clopt('accurate'):
        _("{c.green} removing installed packages due to accurate mode")
        install.remove_installed()

__all__ = ['process_list']
