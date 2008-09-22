#!/usr/bin/env python
import os, os.path
from path import path

create_dir = lambda p: os.path.exists(p) or os.makedirs(p)

def build_workdir(work_dir, rundir, xs, xname, ys, yname, extra='', reps=10):
    argstring = '%d "%s" %s'
    count = len(work_dir.listdir())
    for x in xs:
        for y in ys:
            outdir = rundir / str(x) / str(y)
            for i in range(reps):
                args =  '%d "%s" ' % (i, outdir)
                args += '%s=%s %s=%s ' % (xname, x, yname, y)
                args += extra
                fname = path(work_dir/"%03d-%s=%s_%s=%s-%d" % (
                    count, xname, x, yname, y, i))
                fname.write_text(args)
                count += 1

if __name__ == '__main__':

    # basic values to play with
    loads =   ('load',        [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0])
    sizes =   ('size',        [32,64,128,256,512,1024]) #,2048,4096,8192])
    degrees = ('mean_degree', [4,8,16,32,64])
    reps = 10

    #extra = "mean_degree=64"
    extra = " ttl=1 size=100"

    # exp 1
    name = 'degree-load'
    first = degrees
    second = loads

    # exp 2
    #name   = 'size-load'
    #first = sizes
    #second = loads

    # exp 3
    #name   = 'smallworld'
    #first = ('smallworld_p', [1/float(2**n) for n in [1,2,3,4,5,6,7,8]] + [0])
    #second = loads
    #extra += " topology=smallworld"

    # exp 4
    #name   = 'scalefree'
    #first = ('scalefree_p', [ 0.25 + (0.25*i) for i in range(6)])
    #second = loads
    #extra += " topology=scalefree"

    #name   = 'social'
    #first = ('social_fof', [ 1, 2, 3])
    #second = loads
    #extra += " topology=social"

    root = path('/home/csunix/wavy/')
    rundir = root / "results" / name
    create_dir(rundir)
    build_workdir(root/"work", rundir, first[1], first[0], second[1], second[0], extra, reps)

