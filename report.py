from __future__ import with_statement

import stats
from record import record
import pylab
from draw import plot_eq
import equilibrium
import path
import fcntl
from scripts.util import filelock

def printr(results):

    a = record.counts["GENERAL"]
    b = a + record.counts["GRID"] 
    c = b + record.counts["ECO"] 
    d = c + record.counts["NET"]
    e = d + record.counts["MDS"]

    print "Grid:"
    for k,v in results.items()[:b]:
        print " - %s: %s" % (k,v)
    print

    if record.counts["ECO"]:
        print "Economy:"
        for k,v in results.items()[b:c]:
            print " - %s: %s" % (k,v)
        print

    if record.counts["NET"]:
        print "Network:"
        for k,v in results.items()[c:d]:
            print " - %s: %s" % (k,v)
        print
    
    if record.counts["MDS"]:
        print "MDS:"
        for k,v in results.items()[d:e]:
            print " - %s: %s" % (k,v)
        print


def write(results, out, fname):
    
    fname = out / fname

    write_headers = not fname.exists()

    with filelock(fname) as f:
        if write_headers:
            f.write(',\t'.join(results.keys()))
            f.write('\n')
            f.flush()

        f.write(',\t'.join(str(v) for v in results.values()))
        f.write('\n')


    #plot_eq(record.buys, record.sells)
    #pylab.savefig(out / "eq-real%d.png" %s )
    #pylab.clf()
    #plot_eq(record.buys_theory, record.sells_theory)
    #pylab.savefig("theory.png")



    
