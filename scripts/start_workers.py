#!/usr/bin/env python
import os, os.path, shutil, random, time, sys, fcntl
from itertools import cycle, izip
from path import path

# globals

def isup(host):
    return os.system('ssh -x %s exit > /dev/null 2> /dev/null' % host) == 0

def launch(host, cmd):
    return os.system('ssh -x %s %s &' % (host, cmd))

def init():
    machinefile = open('/home/csunix/wavy/.machinelist')
    machinelist = [l.strip() for l in machinefile if l.strip()]
    return machinelist

if __name__ == '__main__':

    assert len(sys.argv) > 1

    machines = init()

    cmd = "$HOME/sim/deal/scripts/exec.sh python scripts/manager.py " + sys.argv[1]
    for machine in machines:
        if isup(machine):
            print "launcing manager on", machine
            launch(machine, cmd)


