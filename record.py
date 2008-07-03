import math
from collections import defaultdict
from itertools import izip, repeat, chain

import pylab
from SimPy.Simulation import now, Tally
import draw
from util import RingBuffer

buys = []
buys_theory = []
sells = []
sells_theory = []
trade_times = []
trade_prices = []

buyer_timeouts = Tally("buyer_timeouts")
buyer_util = Tally("buyer_util")
seller_util = Tally("seller_util")

njobs = 0

class Tracker(object):
    def __init__(self, name):
        self.name = name
        self.sizes = Tally(name + " job sizes")
        self.limits = Tally(name + " buyer limits")
        self.degrees = Tally(name + " buyer node degrees")

    def record(self, quote):
        self.sizes.observe(quote.job.size)
        self.limits.observe(quote.buyer.limit)
        self.degrees.observe(len(quote.buyer.node.neighbors))

    @property
    def count(self):
        return self.sizes.count()

    def report(self):
        print self._report(self.sizes)
        print self._report(self.limits)
        print self._report(self.degrees)

    def _report(self, tally):
        s = "mean %s: %.2f (%.2f)"
        if tally.count():
            vars = (tally.name, tally.mean(), math.sqrt(tally.var()))
        else:
            vars = (tally.name, 0, 0)
        return s % vars


successes = Tracker("successful")
failures = Tracker("failed")
failed = defaultdict(int)

#void Experiment::record_trade(const Job job,
#                              const Quote& quote,
#                              const Buyer* buyer,
#                              const Seller* seller,
#                              const Time time)
#{
#   if (seller == NULL) {
#      failed_sizes.push_back(job.size);
#      failed_times.push_back(time - job.time);
#      failed_limit_prices.push_back(buyer->limit_price);
#   }
#   else {

#      trades_buyer_actual.push_back(Trade(quote.price, job.work, time));
#      trades_buyer_limits.push_back(Trade(buyer->limit_price, job.work, time));
#      
#      trades_seller_actual.push_back(Trade(quote.price, job.work, time));
#      trades_seller_limits.push_back(Trade(seller->limit_price, job.work, time));

#      allocation_time.push_back(time - job.time);
#      allocated_sizes.push_back(job.size);
#   }
#}


FAIL_JOBSIZE = 0
FAIL_LIMIT = 1
buy_map = defaultdict(list)

def record_trade(quote, success=True):
    global njobs
    njobs += 1
    t = now()

    successes.record(quote)

    #record trade details
    trade = (quote.price, quote.quantity, t)
    trade_times.append(t)
    trade_prices.append(quote.price)
    buys.append(trade)
    sells.append(trade)
    buyer_util.observe(quote.buyer.limit - quote.price)
    seller_util.observe(quote.price - quote.seller.limit)

def record_failure(quote, ninvalid, ntimedout, nrejected):
    global njobs
    njobs += 1
    failures.record(quote)
    nattempted = ntimedout + nrejected
    if nattempted == 0:
        # we attempted no quotes
        if ninvalid > 1: 
            failed["High Limit"] += 1
        else:
            failed["No Quotes"] += 1
    else:
        if nrejected == 0:
            failed["Timeouts"] += 1
        elif ntimedout == 0:
            failed["Busy"] += 1
        else:
            failed["Unkown"] += 1

    

PRICE = 0
QUANT = 1
TIME = 2

def latechain(*iterables):
    for it in iterables:
        i = iter(it)
        for val in i:
            yield val


def pqcurve_iter(buys, sells):
    
    # use static default mutable arg hack, since
    # it seems that generators can't be closures!
    def trade_iter(trades, n_done=[]):
        for t in trades:
            yield t
        #yield t
        n_done.append(0)
        if len(n_done) < 2:
            while 1:
                yield None, None, None

    buys = trade_iter(buys)
    sells = trade_iter(sells)

    bp, bq, bt = buys.next()
    sp, sq, st = sells.next()

    if sp > bp: # no intersect
        raise StopIteration
    else:
        while 1:
            
            if sp and bq > sq:
                point = bp, sp, sq, bt, st
                bq -= sq
                sp, sq, st = sells.next()
            
            elif bp and bq < sq:
                point = bp, sp, bq, bt, st
                sq -= bq
                bp, bq, bt = buys.next()

            else: #sq == bq
                point = bp, sp, max(bq, sq), bt, st
                bp, bq, bt = buys.next()
                sp, sq, st = sells.next()

            yield point
        


def find_equilibrium(buys, sells):
    
    eq_price = 0
    eq_time = 0
    surplus = 0

    found = False
    sell_prices = [0,0]
    buy_prices = [0,0]
    last_bt = last_st = 0

    for buy, sell, q, bt, st in pqcurve_iter(buys, sells):

        if buy is None:
            # reached end of buys
            eq_price = sum(sell_prices) / 2.0
            eq_time = max(last_st, last_bt)
            break

        elif sell is None:
            # reached end of sells
            eq_price = sum(buy_prices) / 2.0
            eq_time = max(last_st, last_bt)
            break

        elif sell > buy:
            # we have crossed the equilibrium point
            eq_price = (buy_prices[1] + sell_prices[1]) / 2.0
            eq_time = last_bt
            break

        else:
            profit = (buy - sell) * q
            surplus += profit
            sell_prices.pop(0)
            sell_prices.append(sell)
            buy_prices.pop(0)
            buy_prices.append(buy)
            last_bt = bt
            last_st = st

    return eq_price, surplus, eq_time


def report():

    # sort all trades
    buys.sort()
    buys.reverse()
    sells.sort()
    buys_theory.sort()
    buys_theory.reverse()
    sells_theory.sort()
    
    real = find_equilibrium(buys, sells)
    plot_eq(buys, sells)
    #draw.supdem(buys, sells)
    pylab.savefig("real.png")
    pylab.clf()
    
    
    theory = find_equilibrium(buys_theory, sells_theory)
    plot_eq(buys_theory, sells_theory)
    #draw.supdem(buys_theory, sells_theory)
    pylab.savefig("theory.png")
    
    #xs, ys = draw.smooth(trade_times, trade_prices, 20)
    #pylab.clf()
    #pylab.plot(xs, ys)
    #pylab.savefig("trades.png")

    #alpha = real[0] / theory[0]
    eff = real[1] / theory[1] * 100
    print "actual eq price: %d" % real[0]
    print "theory eq price: %d" % theory[0]
    print "efficiency: %.2f%%" % eff
    bu = buyer_util.mean()
    su = seller_util.mean()
    print "avg trader util: %d (buyer: %d, seller: %d)" % ((bu+su)/2.0,bu,su)
    print "avg buyer wait: %.2f" % buyer_timeouts.mean()



def plot_eq(buys, sells):
    bx = []
    by = []
    sx = []
    sy = []
    last_q = last_bp = last_sp = max_by = 0
    bdone = False
    sdone = False


    for bp, sp, q, _, _ in pqcurve_iter(buys, sells):

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



    





