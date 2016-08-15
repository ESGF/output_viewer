import unicodedata
import shutil
import os
import re


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)


def nuke_and_pave(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)


def rechmod(path, perms):
    os.chmod(path, perms)
    for path, dirs, files in os.walk(path):
        for f in [os.path.join(path, f) for f in files]:
            os.chmod(f, perms)
        for d in [os.path.join(path, d) for d in dirs]:
            os.chmod(d, perms)
