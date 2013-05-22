
from builder.package import Package
from builder.pset import PackageSet
from builder.utils import gettext as _
from builder import settings
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
            item.priority += 1
            if item in priorities:
                return
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
             if item not in packages:
                raise ValueError(
                    _("FATAL: {0} not found within packages").format(item.name))


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
            ret[loop_name] = map(lambda name: Package(name), kl)
    return ret


def loop_for(packages):
    """Find any known loop that can resolve at least one of stucked packages"""
    packages = set(packages)
    for loop_order, loop_set in __loops_set:
        if packages & loop_set:
            return Loop(loop_order)
    return False


__known_loops = known_loops()
__loops_set = map(lambda s: (s, set(s)), __known_loops.values())
__all__ = ['loop_for', 'Loop']
