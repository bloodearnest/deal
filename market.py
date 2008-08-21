import math
from SimPy.Simulation import Process
import trace

def normalise_price(p):
    """normalise to 2dp"""
    return math.floor((p * 100)+ 0.5) / 100

class MarketRules(object):
    """Dumb continer for market rules, like min/max, NYSE, or timeout info"""
    pass



class Trader(Process):
    def __init__(self, id, rationale):
        Process.__init__(self, "%s %s" % (self.__class__, id))
        self.id = id
        self.rationale = rationale
        self.active = True
        # init price
        self.price = self.rationale.quote()
    
    @property
    def limit(self):
        return self.rationale.limit

    def start_on(self, node):
        self.node = node
        self.init_trading()

    def trade(self):
        raise StopIteration


class Buyer(Trader):
    def __init__(self, id, rationale, job):
        Trader.__init__(self, id, rationale)
        self.job = job

    def remove_from_node(self):
        self.node.buyers.remove(self)
        self.node.buyer_ids.add(self.id)

    def init_trading(self):
        self.node.buyers.add(self)
        self.start(self.trade())

    def finish_trading(self):
        self.remove_from_node()
        self.active = False

    def migrate(self):
        self.remove_from_node()
        
        # choose another node in a different region
        others = [n for n in self.graph.nodes() if n.region != old_node.region]
        other = random.choice(others)

        self.start_on(other)
 
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
    def __init__(self, id, rationale, node):
        Trader.__init__(self, id, rationale)
        self.node = node
    
    @property
    def resource(self):
        return self.node.resource

    def init_trading(self):
        self.start(self.trade())
 
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


