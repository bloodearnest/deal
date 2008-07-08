#!/usr/bin/env python 
import sys, os
import util
from path import path

assert len(sys.argv) > 1

work_dir = path(sys.argv[1])
log_dir = work_dir / "workers"

if not log_dir.exists():
    log_dir.mkdir()
host = os.environ['HOSTNAME'].split('.')[0]
log_file = log_dir / host

f = log_file.open('w')
f.write("manager on %s starting with PID %d\n" % (host, os.getpid()))

while 1:
    args = util.get_next_job(work_dir)
    if args:
        f.write('starting job "%s"\n' % args)
        os.system('exec.sh run.sh ' + args)
        f.write('finished job "%s"\n' % args)
    else:
        f.write("No more work - shuting down\n")
        f.close()
        sys.exit(0)



