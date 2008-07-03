import math
from collections import defaultdict
#from itertools import izip, repeat, chain

from SimPy.Simulation import now, Tally

from util import JobTracker

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

successes = JobTracker("successful")
failures = JobTracker("failed")
failed = defaultdict(int)

def record_trade(quote, success=True):
    global njobs
    njobs += 1
    t = now()

    successes.record(quote)

    # record trade details
    trade = (quote.price, quote.quantity, t)
    trade_times.append(t)
    trade_prices.append(quote.price)
    buys.append(trade)
    sells.append(trade)

    #record utility
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

    




