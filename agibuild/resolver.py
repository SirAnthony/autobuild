# -*- coding: utf-8 -*-

from . import loop
from . import install
from .oset import OrderedSet
from .pset import PackageSet
from .utils import print_array
from .output import (info as _, debug as _d, error as _e)


def get_combined_check_list(build_order, loop_register_data):
    ret = set(build_order)
    for loop_item in loop_register_data:
        ret |= set(loop_item)
    return ret


class Resolver(object):

    def __init__(self, packages):
        if not isinstance(packages, PackageSet):
            raise _e("{c.red}Bad type for package list: {c.yellow}{0}",
                     TypeError, type(packages))
        self.packages = packages

    def init_resolver(self):
        self.step = 0
        self.loop_register = []

        # Initialize build order with packages that have zero dependencies
        build_order = set(filter(lambda p: not p.deps, self.packages))
        unprocessed = set(self.packages) - build_order

        self.build_order = sorted(build_order, key=lambda p: p.name)
        self.unprocessed = sorted(sorted(unprocessed, key=lambda p: p.name),
                                  lambda p1, p2: cmp(p2.priority, p1.priority))

    def log_step(self, part):
        _d("{c.white}Step {c.bold}{c.yellow}{0}{c.end}{c.white}/part "
           "{c.bold}{c.yellow}{1}{c.end}, in queue: {c.cyan}{2}{c.white}"
           " packages, enqueued: {c.green}{3}{c.white}.",
           self.step, part, len(self.unprocessed), len(self.build_order))

    def resolve_loop(self, l):
        # Check if loop_order is resolvable by build_order and loop_order
        if l.processed or not l.resolvable_by(self.build_order):
            return 0

        loop_set = set(l)
        stuck_position = l.position
        build_order = self.build_order
        unprocessed = self.unprocessed

        _d("\n\n\n{0}Loop order detected to be resolvable. Loop itself:{0}",
           '-'*11)
        print_array(l, _d)
        _d("{0}Build order:{0}", '='*31)
        print_array(build_order, _d)
        _d("{0}\n\n", '-'*74)

        # Add loop depends
        merge_position = len(build_order)
        build_order.extend(l)

        # Remove packages from queue
        for item in loop_set:
            if item in unprocessed:
                unprocessed.remove(item)

        # Re-add packages that were between and depend on loop
        for index in range(stuck_position, merge_position):
            pkg = build_order[index]
            if loop_set & pkg.deps:
                build_order.append(pkg)

        _d("Finished loop")
        l.processed = True
        self.loop_register.remove(l)

        return len(l) + (merge_position - stuck_position)

    def check_loops(self):
        # Debug check (catches a case when in_queue is calculated incorrectly
        build_order = self.build_order
        unprocessed = self.unprocessed
        if not unprocessed:
            raise _e("CODE ERROR: Loop detected, but no loop really exist.",
                     ValueError)

        # Find a known loop which contains at least one of stucked packages
        loop_order = loop.loop_for(unprocessed, self.loop_register)

        if not loop_order:
            print_array(loop_order, _d)
            raise _e("Unresolvable loop detected, fix known loops and try "
                     "again", ValueError)

        # Throw error if loop is invalid
        loop_order.check_valid(self.packages)

        # Add loop deps
        order_set = PackageSet(loop_order)
        deps = filter(lambda x: x not in build_order and
                      x not in unprocessed and x not in loop_order,
                      order_set.get_dep_tree(install.build()))
        self.unprocessed.extend(deps)

        loop_order.position = len(self.build_order)
        self.loop_register.append(loop_order)
        _d("Registering loop: {0}. Total loops count: {1}", loop_order,
           len(self.loop_register))

    def advance_loops(self):
        ret = 0
        build_order = self.build_order
        for item in self.loop_register:
            ret += self.resolve_loop(item)
        return ret

    def check_ready(self):
        """
Checking each package if it is ready to be added to build_order.
It means:
  1) not in build_order already,
  2) all of his deps are already there
If success, package is added to build_order
"""

        count = 0
        unprocessed = self.unprocessed
        build_order = self.build_order
        check_array = get_combined_check_list(build_order, self.loop_register)

        def add_package(package):
            if package in check_array or \
                    not package.enqueue(build_order, self.loop_register):
                return 0
            _d("{c.green}ADDING: {c.cyan}{0}", package.name)
            unprocessed.remove(package)
            check_array.add(package)
            build_order.append(package)
            # Add package twice if it depends on itself
            if package._twice:
                build_order.append(package)
            # Check for resolved loops
            for l in package.in_loop:
                self.resolve_loop(l)
            return 1

        # Packages have priority to be enqueued if it blocks resolving.
        # First process all priority packages:
        priorities = OrderedSet(filter(lambda x: x.priority, unprocessed))
        check_len = len(check_array)
        while len(priorities):
            priorities -= check_array
            for package in priorities:
                count += add_package(package)
            if len(check_array) == check_len:
                # We in loop
                break
            check_len = len(check_array)

        # next process other packages
        for package in unprocessed[:]:
            count += add_package(package)

        return count

    def _next(self):
        self.step += 1
        self.log_step(self.step)
        this_move = False
        step_move = self.check_ready()
        if step_move > 0:
            this_move = True
            _d("{c.white}Part 1: move {c.yellow}{0}", step_move)

        # At this point, try to advance with loops
        loop_move = self.advance_loops()
        if loop_move:
            this_move = True
            _d("{c.white}Part 2 (LOOP): move {c.yellow}{0}", loop_move)

        # Checking counters: we need to find out is there any advance in
        # previous step. If old and current sizes match - no advance was
        # made. It means, that we are stuck on a dependency loop
        if not this_move:
            self.check_loops()
            this_move = True

    def resolve(self):
        self.init_resolver()
        while len(self.unprocessed):
            self._next()
        return self.build_order
