
from builder import settings
from utils import gettext as _
import os


_default_path = ""


def get_gitpath(path):
    pass


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
