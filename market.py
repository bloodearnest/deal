import math
from SimPy.Simulation import Process

def normalise_price(p):
    """normalise to 2dp"""
    return math.floor((p * 100)+ 0.5) / 100

class MarketRules(object):
    """Dumb continer for market rules, like min/max, NYSE, or timeout info"""
    pass


class Trader(Process):
    def __init__(self, id, node, rationale):
        Process.__init__(self, "%s %s" % (self.__class__, id))
        self.id = id
        self.node = node
        self.rationale = rationale
        self.active = True
        # init price
        self.price = self.rationale.quote()
    
    @property
    def limit(self):
        return self.rationale.limit


class Buyer(Trader):
    def __init__(self, id, node, rationale):
        Trader.__init__(self, id, node, rationale)
        node.buyers.add(self)

    def cleanup(self):
        self.node.buyers.remove(self)
        self.active = False
        self.node.buyer_ids.add(self.id)
 
    # utility function
    def create_quote(self):
        self.price = self.rationale.quote()
        return Bid(self, None, self.job, self.price)

    def create_accept(self, quote):
        return Bid(self, quote.seller, self.job, quote.price)

    def viable_quote(self, q):
        return (self.active and 
                q.ask and 
                q.price <= self.price and 
                q.size >= self.job.size)


class Seller(Trader):
    def __init__(self, id, node, rationale):
        Trader.__init__(self, id, node, rationale)
    
    @property
    def resource(self):
        return self.node.resource
 
    # utility function
    def create_quote(self):
        self.price = self.rationale.quote()
        return Ask(None, self, self.resource.free, self.price)

    def create_accept(self, quote):
        return Ask(quote.buyer, self, quote.job, quote.price)

    def viable_quote(self, q):
        return (self.active and
                self.bid and
                q.price >= self.price and
                q.size <= self.node.resource.free)


