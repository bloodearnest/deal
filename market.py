import math
from SimPy.Simulation import Process

def normalise_price(p):
    """normalise to 2dp"""
    return math.floor((p * 100)+ 0.5) / 100

class MarketRules(object):
    """Dumb continer for market rules, like min/max, NYSE, or timeout info"""
    pass


class Buyer(Process):
    def __init__(self, id, node):
        Process.__init__(self, "%s %s" % (self.__class__, id))
        self.id = id
        self.node = node
        self.active = True
        node.buyers.add(self)

    def cleanup(self):
        self.node.buyers.remove(self)
        self.active = False
        self.node.buyer_ids.add(self.id)
    
    @property
    def limit(self):
        return self.rationale.limit


class Seller(Process):
    @property
    def limit(self):
        return self.rationale.limit
