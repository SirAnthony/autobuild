# -*- coding: utf-8 -*-

from builder import loop
from builder.functions import print_array
from builder.oset import OrderedSet
from builder.pset import PackageSet
from builder.utils import gettext as _
import logging


def get_combined_check_list(build_order, loop_register_data):
    ret = set(build_order)
    for loop_item in loop_register_data:
        ret |= set(loop_item)
    return ret



class Resolver(object):

    def __init__(self, packages):
        if not isinstance(packages, PackageSet):
            raise TypeError(_("Bad type for package list"))
        self.packages = packages


    def init_resolver(self):
        self.step = 0
        self.unprocessed = OrderedSet()
        self.build_order = []
        self.loop_register = []
        for package in self.packages:
            if not package.deps:
                # Initialize build order with packages that have zero dependencies
                self.build_order.append(package)
            else:
                self.unprocessed.add(package)


    def log_step(self, part):
        logging.info(_("Step %s/part %s, in queue: %s packages, enqueued: %s"),
                self.step, part, len(self.unprocessed), len(self.build_order))


    def resolve_loop(self, l):
        # Check if loop_order is resolvable by build_order and loop_order
        if l.processed or not l.resolvable_by(self.build_order):
            return 0

        loop_set = set(l)
        stuck_position = l.position
        build_order = self.build_order

        logging.debug("\n\n\n{0}Loop order detected to be resolvable. Loop itself:{0}".format('-' * 11))
        print_array(l, logging.debug)
        logging.debug("{0}Build order:{0}".format('='*31))
        print_array(build_order, logging.debug)
        logging.debug("{0}\n\n".format('-'*74))

        # Add loop depends
        merge_position = len(build_order)
        build_order.extend(l)

        # Remove packages from queue
        self.unprocessed -= loop_set

        # Re-add packages that were between and depend on loop
        for index in range(stuck_position, merge_position):
            pkg = build_order[index]
            if loop_set & pkg.deps:
                build_order.append(pkg)

        logging.debug("Finished loop")
        l.processed = True
        self.loop_register.remove(l)

        return len(l) + (merge_position - stuck_position)


    def check_loops(self):
        # Debug check (catches a case when in_queue is calculated incorrectly
        if not self.unprocessed:
            raise ValueError(_("CODE ERROR: Loop detected, but no loop really exist."))

        # Find a known loop which contains at least one of stucked packages
        loop_order = loop.loop_for(self.unprocessed, self.loop_register)

        if not loop_order:
            print_array(loop_order, logging.debug)
            raise ValueError(_("Unresolvable loop detected, fix known loops and try again"))

        # Throw error if loop is invalid
        loop_order.check_valid(self.packages)

        loop_order.position = len(self.build_order)
        self.loop_register.append(loop_order)
        logging.debug(_("Registering loop: %s"), len(self.loop_register))


    def advance_loops(self):
        ret = 0
        build_order = self.build_order
        for item in self.loop_register:
            ret += self.resolve_loop(item)
        return ret


    def check_ready(self):
        # Checking each package if it is ready to be added to build_order.
        # It means that it is:
        #  1) not in build_order already,
        #  2) all of his deps are already there
        # If success, package is added to build_order
        check_array = get_combined_check_list(self.build_order, self.loop_register)
        count = 0

        def add_package(package):
            if package in check_array or \
                    not package.enqueue(check_array):
                return 0
            self.unprocessed.remove(package)
            check_array.add(package)
            self.build_order.append(package)
            # Add package twice if it depends on itself
            if package._twice:
                self.build_order.append(package)
            # Check for resolved loops
            for l in package.in_loop:
                self.resolve_loop(l)
            return 1

        # Packages have priority to be enqueued if it blocks resolving.
        # First process all priority packages:
        priorities = OrderedSet(filter(lambda x: x.priority, self.unprocessed))
        check_len = len(check_array)
        while len(priorities):
            priorities -= check_array
            for package in priorities:
                count += add_package(package)
            if len(check_array) == check_len:
                break # We in loop
            check_len = len(check_array)

        # next process other packages
        for package in self.unprocessed:
            count += add_package(package)

        return count

    def _next(self):
        self.step += 1
        self.log_step(self.step)
        this_move = False
        self.unprocessed = OrderedSet(sorted(
            sorted(self.unprocessed, key=lambda p: p.name),
                lambda p1, p2: cmp(p2.priority, p1.priority)))
        step_move = self.check_ready()
        if step_move > 0:
            this_move = True
            logging.info(_("Part 1: move %s"), step_move)

        # At this point, try to advance with loops
        loop_move = self.advance_loops()
        if loop_move:
            this_move = True
            logging.info("Part 2 (LOOP): move %s", loop_move)

        # Checking counters: we need to find out is there any advance in previous step
        # If old and current sizes match - no advance was made.
        # It means, that we are stuck on a dependency loop
        if not this_move:
            self.check_loops()
            this_move = True

    def resolve(self):
        self.init_resolver()
        #import pudb; pudb.set_trace()
        while len(self.unprocessed):
            self._next()
        return self.build_order
