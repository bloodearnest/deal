import sys
from pprint import pprint
from scipy import *
from pylab import *
import matplotlib.axes3d as p3
from path import path

def all_equal(i):
    it = iter(i)
    x = it.next()
    for next in it:
        if x != next:
            return False
    return True


def my_mean(a):
    if a.dtype.kind == 'S':
        assert all_equal(a)
        return a[0].strip()
    else:
        return a.mean()

def process_runs(dir):
    raw_file = dir / 'raw.dat'
    try:
        raw = mlab.csv2rec(raw_file)
        print "Loading file:", raw_file
    except:
        print "Bad file:", raw_file
        return None, None
    record = tuple(my_mean(raw[n]) for n in raw.dtype.names)
    return record, raw.dtype.names

def process_stats(dir):
    recs = []
    names = None
    x = y = 0
    for xdir in sorted(dir.listdir()):
        x+= 1
        for ydir in sorted(xdir.listdir()):
            y += 1
            record, _names = process_runs(ydir)
            if record:
                recs.append(record)
                if names:
                    assert names == _names
                else:
                    names = _names

    results = rec.fromrecords(recs, names=names)
    return results, (x,y/x)

def plot_2d(stats, shape, x, y, z, name):
    X = reshape(stats[x], shape)
    Y = reshape(stats[y], shape)
    Z = reshape(stats[z], shape)

    for i, zs in enumerate(Z[:,0]):
        plot(X[i], Y[i], label=z+'='+str(zs) )

    legend()
    savefig(name + ".png")
    clf()


if __name__ == '__main__':

    results_dir = path(sys.argv[1])
    stats, shape = process_stats(results_dir)
    #plot_2d(stats, shape, 'load', 'resource_util', 'size', 'util')
    save(results_dir / 'results.out', stats, fmt='%s', delimiter=',')

