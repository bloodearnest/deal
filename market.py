import math, random
from SimPy.Simulation import Process, hold
from trace import Tracer

def normalise_price(p):
    """normalise to 2dp"""
    return math.floor((p * 100)+ 0.5) / 100

class MarketRules(object):
    """Dumb continer for market rules, like min/max, NYSE, or timeout info"""
    pass



class Trader(Process):
    def __init__(self, id, rationale):
        Process.__init__(self, "%s %d" % (self.__class__, id))
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
        self.trace and self.trace("starting on %s" % node)

    def trade(self):
        raise StopIteration

    def __str__(self):
        return "%s %d" % (self.__class__.__name__, self.id)


class Buyer(Trader):
    def __init__(self, id, rationale, job):
        Trader.__init__(self, id, rationale)
        self.job = job
        self.migrations = 0

    def remove_from_node(self):
        self.trace and self.trace("removing from %s" % self.node)
        self.node.buyers.remove(self)
        self.node.buyer_ids.add(self.id)

    def init_trading(self):

        # set up trace for new node
        self.trace = Tracer(self.node)
        self.trace = self.trace.add('%-12s' % self)
        self.trace = self.trace.add('j%-5d' % self.job.id)

        # add to new node
        self.node.buyers.add(self)

        self.process = self.TradeProcess(self)
        self.process.start(self.process.trade())

    def finish_trading(self):
        self.remove_from_node()
        self.active = False

    class CancelProcess(Process):
        def pem(self, process):
            yield hold, self, 0.00001
            self.cancel(process)


    def migrate(self):
        self.trace and self.trace("migrating")
        self.remove_from_node()
        
        # choose another node in a different region
        others = [n for n in self.node.graph.nodes_iter() 
                  if n.region != self.node.region]
        other = random.choice(others)

        #cancel any events (there shouldn't be, but just in case)
        p = self.CancelProcess()
        p.start(p.pem(self.process))

        self.trace and self.trace("moving to %s" % other)
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
        self.trace = Tracer(node)
        self.trace = self.trace.add('%-12s' % self)
    
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


