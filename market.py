import math
from SimPy.Simulation import Process

def normalise_price(p):
    """normalise to 2dp"""
    return math.floor((p * 100)+ 0.5) / 100


class Quote(object):
    """A quote in the market"""
    def __init__(self, bid, buyer, seller, job, price):
        self.seller = seller
        self.buyer = buyer
        self.bid = bid
        self.ask = not bid
        self.price = price
        self.job = job
        self.quantity = job.quantity

    def __eq__(self, other):
        return (self.price == other.price and
                self.job == other.job)

    def __str__(self):
        return 'q(%.2f, j%d)' % (self.price/100.0, self.job.id)

    def str(self, receiver):
        other = receiver == self.buyer and self.seller or self.buyer
        return "%s from %s at %s" % (self, other, other.node)

def Bid(*a, **kw):
    """Factory for a Bid quote"""
    return Quote(True, *a, **kw)

def Ask(*a, **kw):
    """Factory for an Ask quote"""
    return Quote(False, *a, **kw)


class Trade(object):
    """Record of a trade"""
    def __init__(self, buyer, seller, quote, time):
        pass

class MarketRules(object):
    """Dumb continer for market rules, like min/max, NYSE, or timeout info"""
    pass


class Buyer(Process):
    @property
    def limit(self):
        return self.rationale.limit

class Seller(Process):
    @property
    def limit(self):
        return self.rationale.limit
