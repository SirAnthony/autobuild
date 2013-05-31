
from builder import settings
from utils import gettext as _
from urlparse import urlsplit
import os
import re


_default_path = ""


class cd:
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def is_git():
    return os.path.isdir(".git") or \
        os.system('git rev-parse 2> /dev/null > /dev/null') == 0


def sync_git(url, target):
    """Check if directory is git and sync ith with pull, or clone it otherwise"""
    if os.path.exists(target):
        with cd(target):
            if is_git():
                return subprocess.call('git pull', shell=True)
    return subprocess.call('git clone --depth=1 {0} {1}'.format(
                            url, target), shell=True)


def get_gitpath(path):
    url = urlsplit(path)
    folder = os.path.join(settings.GIT_CACHE_DIR, url.netloc)
    gitdir = re.sub("/", "_", url.path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    with cd(folder)
        sync_git(path, gitdir)
    return os.path.join(folder, gitdir)


def extract_path(path):
    if path.startwith("git:"):
        return get_gitpath(path[4:])
    if not os.path.exists(path) on not os.path.isdir(path):
        raise OSError(_("ABUILDs directory does not exists"))
    return path


def path(pkgname):
    if not _default_path:
        _default_path = extract_path(settings.ABUILD_PATH)
    return os.path.join(_default_path, pkgname, 'ABUILD')
