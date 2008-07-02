from itertools import izip

import pylab
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

