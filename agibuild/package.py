# -*- coding: utf-8 -*-

from . import settings, config
from .abuild import Abuild, AbuildError
from .adict import AttrDict
from .mset import MergableSet
from .skyfront import SkyFront
from .output import (info as _,
                     debug as _d,
                     warn as _w,
                     error as _e )
from mpkg.support import compareVersions
import os.path



PKG_STATUS_NAMES = ('build', 'keep', 'install', 'missing')
PKG_STATUS = AttrDict([(name, n) for n, name in enumerate(PKG_STATUS_NAMES)])
PKG_STATUS_STR = AttrDict([(name, name) for name in PKG_STATUS_NAMES])




mpkg_db = SkyFront('sqlite', '/var/mpkg/packages.db')


class PackageMeta(type):

    _cache = {}
    _provides = {}

    def __call__(cls, name, claimer=None, *args, **kwargs):
        """Create only one instance per package"""

        if name in cls._cache:
            return cls._cache[name]

        package = super(PackageMeta, cls).__call__(name, *args, **kwargs)

        # Have alternatives
        if not package.get_abuild(False) and name in cls._provides:
            provider = cls._provides[name]
            if not claimer or claimer.name == name:
                return provider
            _w("""{c.yellow}Looks like one package ({c.cyan}{0}"""\
               """{c.yellow}) ot its base package in provides of another """\
               """({c.cyan}{1}{c.yellow}) but both selected to build. """\
               """Behaviour of this case is undefined, build may fails """\
               """eventually.""", name, provider.name)



        cls._cache[name] = package
        return package


    @classmethod
    def fetch_provides(cls):
        stat, data = mpkg_db.getRecords('packages', ['package_name'],
                         package_provides=['', 'IS NOT'])
        if not stat:
            raise _e("{c.red}Unexpected result while fetching db: {0}",
                       ValueError, data)

        # Just toch it, abuild call will do all things.
        for p in map(lambda x: x[0], data):
            Package(p).get_abuild(False)


    @classmethod
    def fetch_versions(cls):
        names = [p.name for p in cls._cache.values()]
        names_query = sum([[i, '='] for i in names], [])
        stat, data = mpkg_db.getRecords('packages', ['package_name',
                'package_version', 'package_build', 'package_installed'],
                        _skyfront_and=False, package_name=names_query)
        if not stat:
            raise _e("{c.red}Unexpected result while fetching db: {0}",
                       ValueError, data)

        for p in data:
            name, ver, inst = p[0], p[1:3], p[3]
            pkg = cls._cache.get(name, None)
            if not pkg:
                _w('{c.yellow}Selected wrong package{c.cyan}{0}', name)
                continue
            if inst:
                pkg._installed = ver
            if not hasattr(pkg, '_avaliable_list'):
                pkg._avaliable_list = []
            pkg._avaliable_list.append(ver)

    @classmethod
    def fetch_dependencies(cls, pkgset):
        names = [p.name for p in pkgset]
        names_query = sum([[i, '='] for i in names], [])
        stat, data = mpkg_db.getRecords('dependencies', [
            'dependency_package_name', 'package_name'],
            'LEFT OUTER JOIN `packages` on `package_id` = `packages_package_id`',
            package_installed=1, dependency_package_name=[names_query, 'OR'])
        if not stat:
            raise _e("{c.red}Unexpected result while fetching db: {0}",
                       ValueError, data)
        for pkgname, depname in data:
            package = Package(pkgname)
            if not hasattr(package, '_dependants'):
                package._dependants = set()
            package._dependants.add(Package(depname))


class Package(object):
    __metaclass__ = PackageMeta

    def __init__(self, name):
        #if getattr(self, "_init", False):
        #    return
        self._init = True
        self.name = name
        self._twice = False
        self.priority = 0
        self.in_loop = []
        self.dep_for = set()

    def __str__(self):
        return "Package {0}".format(self.name)
    def __unicode__(self):
        return unicode(self.__str__())
    def __repr__(self):
        return self.__unicode__()

    def get_abuild(self, signalize=True):
        if not hasattr(self, '_abuild'):
            self._abuild = abuild = Abuild(self.name)
            if not abuild:
                if signalize:
                    _e("{c.red}Abuild for {0} not found of contains errors.",
                        None, self.name)
            elif abuild.provides:
                self.__metaclass__._provides[abuild.provides] = self
        return self._abuild
    abuild = property(get_abuild)

    @property
    def base(self):
        if self.abuild and self.abuild.pkgname != self.name:
            return Package(self.abuild.pkgname)
        return self

    @property
    def deps(self):
        if not self.abuild_exist:
            return frozenset()
        if not hasattr(self, '_deps'):
            self._deps = MergableSet(map(lambda p: Package(p),
                filter(lambda n: n and n not in settings.BLACKLIST_PACKAGES,
                self.abuild.build_deps)))
            self._deps.merge(lambda p: p.abuild and p.name != p.abuild.pkgname,
                             lambda p: Package(p.abuild.pkgname))
            if self in self._deps:
                self._deps.remove(self)
                self._twice = True
            for dep in self._deps:
                dep.dep_for.add(self)
        return self._deps

    @property
    def installdeps(self):
        if not self.abuild_exist:
            return frozenset()
        if not hasattr(self, '_install_deps'):
            self._install_deps = MergableSet(map(lambda p: Package(p),
                filter(lambda n: n and n not in settings.BLACKLIST_PACKAGES,
                self.abuild.adddep)))
            self._install_deps.merge(lambda p: p.abuild and p.name != p.abuild.pkgname,
                             lambda p: Package(p.abuild.pkgname))
        return self._install_deps

    @property
    def dependants(self):
        return getattr(self, '_dependants', frozenset())

    @property
    def installed(self):
        if not hasattr(self, '_installed'):
            stat, data = mpkg_db.getRecords('packages',
                        ['package_version', 'package_build'], limit=1,
                        package_name=self.name, package_installed=1)
            self._installed = data[0] if data else ()
        return self._installed

    @property
    def avaliable(self):
        if not hasattr(self, '_avaliable'):
            if hasattr(self, '_avaliable_list'):
                self._avaliable = reduce(lambda av, pkg: av if \
                        compareVersions(str(av[0]), str(av[1]),
                        str(pkg[0]), str(pkg[1])) > 0 else pkg,
                        self._avaliable_list)
            else:
                stat, data = mpkg_db.getRecords('packages',
                                ['package_version', 'package_build'],
                                limit=1, package_name=self.name)
                self._avaliable = data[0] if data else ()
        return self._avaliable


    @property
    def abuild_exist(self):
        return bool(self.abuild)

    @property
    def buildable(self):
        return self.abuild_exist

    @property
    def updatable(self):
        if not hasattr(self, '_updatable'):
            self._updatable = self.vercmp(*self.installed)
        return self._updatable > 0

    def enqueue(self, build_order, loops=[]):
        """Check if all deps in build_order"""
        # Check if needed for loop
        self_loops = filter(lambda x: x in self.in_loop, loops)
        loop_packages = [item for s in self_loops for item in s]
        diff = set(self.deps) - set(build_order + loop_packages)
        if not diff:
            _d("{c.white}ALL DEPS OK: {c.cyan}{0}{c.white} is ready", self.name)
            return True
        _d("{c.yellow}DEP FAIL: {c.cyan}{0}{c.yellow} => {c.cyan}{1}",
                self.name, ', '.join([d.name for d in diff]))
        return False


    def vercmp(self, version, build):
        """Compare supplied version and build with current abuild version"""
        if not self.abuild:
            return -1
        if not config.clopt('enable_vcs'):
            for vcs in ('cvs', 'svn', 'git', 'hg'):
                version = version.split('_' + vcs)[0]
        return compareVersions(str(self.abuild.pkgver), str(self.abuild.pkgbuild),
                               str(version), str(build))


    def action(self, force):
        #if self.name == "bluez-firmware":
        #    import pudb; pudb.set_trace()
        if self in force:
            if self.buildable:
                return PKG_STATUS_STR.build
        elif self.installed:
            if config.clopt('update') and self.updatable:
                return PKG_STATUS_STR.build
            return PKG_STATUS_STR.keep
        elif self.avaliable and not config.clopt('skip_install'):
            return PKG_STATUS_STR.install
        elif self.buildable:
            return PKG_STATUS_STR.build
        return PKG_STATUS_STR.missing


    def output(self, status):
        if status == PKG_STATUS_STR.missing or config.clopt('list_order'):
            version = ''
        elif status == PKG_STATUS_STR.install:
            version = '[{0}-{1}]'.format(*self.avaliable)
        elif status == PKG_STATUS_STR.keep:
            version = '[{0}-{1}]'.format(*self.installed)
        else:
            ovstr = ''
            vstr = '{0}-{1}'.format(self.abuild.pkgver, self.abuild.pkgbuild)
            if self.installed:
                if self.updatable:
                    ovstr = '{0}-{1} -> '.format(*self.installed)
                else:
                    ovstr = '[{c.version}' + vstr + '{c.old_version}]'
                    vstr = ''
            version = ''.join(['{c.old_version}', ovstr, '{c.version}', vstr])

        depends = ''
        if self.dep_for:
            do_dep = getattr(settings, 'PRINT_DEPENDS', False)
            if do_dep or status == PKG_STATUS_STR.missing:
                depends = [' <={c.miss_dep}']
                depends.extend([p.name for p in self.dep_for])
                depends.append('{c.end}')
                depends = ' '.join(depends)

        return ''.join([self.name, ' {c.version}', version, '{c.end}',
                        depends])
