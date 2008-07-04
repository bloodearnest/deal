import pylab
import stats
import record
from draw import plot_eq
import equilibrium
import path
import fcntl

def printr(results):

    a = record.counts["GENERAL"]
    b = a + record.counts["GRID"] 
    c = b + record.counts["ECO"] 

    print "Grid:"
    for k,v in results.items()[a:b]:
        print " - %s: %0.2f" % (k,v)

    print
    print "Economy:"
    for k,v in results.items()[b:]:
        print " - %s: %0.2f" % (k,v)

    plot_eq(record.buys, record.sells)
    pylab.savefig("real.png")
    pylab.clf()
    plot_eq(record.buys_theory, record.sells_theory)
    pylab.savefig("theory.png")

def write(results, fname):

    fname = path.path(fname)

    write_headers = not fname.exists()
    f = open(fname, 'a')
    fcntl.flock(f, fcntl.LOCK_EX)

    if write_headers:
        f.write(',\t'.join(results.keys()))
        f.write('\n')
        f.flush()

    f.write(',\t'.join(str(v) for v in results.values()))
    f.write('\n')

    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()



    
