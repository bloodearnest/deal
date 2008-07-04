from itertools import izip
import networkx
import pylab
from stats import dists

import equilibrium

PRICE = 0
QUANT = 1

def smooth(x, y, n):
    xs = []
    ys = []
    iter = izip(x, y)
    t, p = iter.next()
    m = int(max(x))
    for i in range(0, m, m/n):
        s = []
        while t < i:
            s.append(p)
            t, p = iter.next()
        if s:
            xs.append(i)
            ys.append(sum(s)/float(len(s)))
    return xs, ys


def pqcurve(data):
    xs = []
    ys = []
    q = 0
    p = 0
    for x in data:
        xs += [q, q]
        ys += [p, x[PRICE]]
        q += x[QUANT]
        p = x[PRICE]

    m = min(len(xs), len(ys))
    pylab.plot(xs[:m], ys[:m], '--')


def supdem(buys, sells):
    pqcurve(buys)
    pqcurve(sells)


def topology(g):
    if g.size() > 30:
        print "Not drawing topology as size > 30"
    else:
        networkx.draw(g, pos=networkx.circular_layout(g))
        pylab.savefig("topology.png")
        pylab.clf()

def plot_eq(buys, sells):
    bx = []
    by = []
    sx = []
    sy = []
    last_q = last_bp = last_sp = max_by = 0
    bdone = False
    sdone = False


    for bp, sp, q, _, _ in equilibrium.pqcurve_iter(buys, sells):

        if bp:
            bx += [last_q, last_q]
            by += [last_bp, bp]
            max_by = max(max_by, bp)

        if sp:
            sx += [last_q, last_q]
            sy += [last_sp, sp]

        last_q += q
        last_bp = bp
        last_sp = sp

    #bx.append(bx[-1])
    #by += [0]

    #sx.append(sx[-1])
    #sy += [max_by]

    pylab.plot(bx, by)
    pylab.plot(sx, sy)



    





