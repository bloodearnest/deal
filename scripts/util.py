from __future__ import with_statement

from contextlib import contextmanager
import fcntl, os, time
from path import path

@contextmanager
def filelock(path, mode="a+", type=fcntl.LOCK_EX, block=False):
    f = open(path, mode)
    if not block:
        type |= fcntl.LOCK_NB
    fcntl.flock(f, type)
    try:
        yield f
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()


def host_is_up(host):
    return os.system('ssh -x %s exit > /dev/null 2> /dev/null' % host) == 0

def run_on_host(host, cmd):
    return os.system('ssh -x %s "%s" &' % (host, cmd))

def get_next_job(dir):
    dir = path(dir)
    # big jobs first!
    for fname in reversed(sorted(dir.listdir(), key=lambda f: f.name)):
        try:
            with filelock(fname) as f:
                line = f.read()
                fname.unlink()
                return line
        except IOError: # either already locked or does not exist
            pass
    




