#!/usr/bin/env python 
import sys, os
import util
from path import path

assert len(sys.argv) > 1

work_dir = path(sys.argv[1])
log_dir = work_dir.parent / "workers"

if not log_dir.exists():
    log_dir.mkdir()
host = os.uname()[1].split('.')[0]
log_file = log_dir / host

f = log_file.open('w')
f.write("manager on %s starting with PID %d\n" % (host, os.getpid()))
f.flush()
while 1:
    args = util.get_next_job(work_dir)
    if args:
        f.write('starting job "%s"\n' % args)
        f.flush()
        retcode = os.system('deal/scripts/exec.sh deal/scripts/run.sh ' + args)
        if retcode == 0:
            f.write('finished.')
        else:
            f.write('ERROR: job finished with exit code %d\n' % retcode)
        f.flush()
    else:
        f.write("No more work - shuting down\n")
        f.close()
        sys.exit(0)



