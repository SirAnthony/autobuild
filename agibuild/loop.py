# -*- coding: utf-8 -*-

from . import settings
from .output import error as _e
from .package import Package
from .pset import PackageSet
import os
import re


class Loop(list):

    def __init__(self, *args, **kwargs):
        self.position = 0
        self.processed = False
        super(Loop, self).__init__(*args, **kwargs)
        self.mark_packages()

    def mark_packages(self):
        """Increase priority of dependences to faster loop resolving."""
        priorities = set()
        def increase_priority(item):
            if item in priorities:
                return
            item.priority += 1
            item.in_loop.append(self)
            priorities.add(item)
            for dep in item.deps:
                increase_priority(dep)

        for item in self:
            if not isinstance(item, Package):
                raise TypeError(_('Loop must contain packages only'))
            increase_priority(item)


    def check_valid(self, packages):
        for item in self:
            if item not in packages and not item.abuild:
                _e("""{c.red}Package {c.yellow}{0}{c.red} was """\
                   """specified in loop but was not found. Aborting.""",
                   None, item.name)
                raise _e("""{c.red}FATAL: {c.yellow}{0}{c.red} not """\
                    """found within packages.""", ValueError, item.name)

    def resolvable_by(self, processed_packages):
        for package in self:
            if package in processed_packages:
                continue
            if not package.enqueue(processed_packages + self):
                return False
        return True



def known_loops():
    """Reads all known loops"""
    files = os.listdir(settings.LOOPS_PATH)
    ret = {}
    for loop_name in files:
        if loop_name in settings.BLACKLIST_LOOPS:
            continue
        loop_path = os.path.join(settings.LOOPS_PATH, loop_name)
        with open(loop_path, 'r') as handler:
            known_loop = handler.read().splitlines()
            kl = filter(None,
                [re.sub('#.*', '', k).strip() for k in known_loop])
            ret[loop_name] = map(lambda name: Package(name).base, kl)
    return ret


def loop_for(packages, exist_loops):
    """Find any known loop that can resolve at least one of stucked packages"""
    packages = set(packages)
    global __loops_set
    if not __loops_set:
        global __known_loops
        __known_loops = known_loops()
        __loops_set = map(lambda s: (s, set(s)), __known_loops.values())
    # Remove already counted packages
    for l in exist_loops:
        packages -= set(l)
    for loop_order, loop_set in __loops_set:
        if packages & loop_set:
            return Loop(loop_order)
    return False


#__known_loops =  known_loops()
__loops_set = None # map(lambda s: (s, set(s)), __known_loops.values())
__all__ = ['loop_for', 'Loop']
