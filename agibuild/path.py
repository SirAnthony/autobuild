# -*- coding: utf-8 -*-

from . import settings
from .output import error as _e
from urlparse import urlsplit
import os
import re


class cd:
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)



class Path(object):

    def __init__(self, path):
        self.localpath = self.resolve(path)
        self._dir = ""

    def resolve(self, path):
        return path

    def check(self):
        if not os.path.exists(self.localpath) or not os.path.isdir(self.localpath):
            raise _e("{c.red}Directory does not exists: {c.magnetta}{0}",
                    OSError, self.localpath)


class GitPath(Path):

    def __init__(self, url):
        self.url = url
        super(GitPath, self).__init__(url)


    def resolve(self, path):
        url = urlsplit(path)
        folder = os.path.join(settings.GIT_CACHE_DIR, url.netloc)
        gitdir = re.sub("/", "_", url.path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with cd(folder):
            self.sync(path, gitdir)
        return os.path.join(folder, gitdir)


    def sync(self, base, target):
        """Check if directory is git and sync ith with pull, or clone it otherwise"""
        if os.path.exists(target):
            with cd(target):
                if is_git():
                    return subprocess.call('git pull', shell=True)
        return subprocess.call('git clone --depth=1 {0} {1}'.format(
                            url, target), shell=True)

    @staticmethod
    def is_git():
        return os.path.isdir(".git") or \
            os.system('git rev-parse 2> /dev/null > /dev/null') == 0


def guess_path(path):
    if path.startswith("git:"):
        path = GitPath(path[4:])
    else:
        path = Path(path)
    path.check()
    return path
