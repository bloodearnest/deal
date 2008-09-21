from SimPy.Simulation import now
from trace import Tracer
from processes import *
from trader import Trader
from agents import ResourceAgent


class Seller(ResourceAgent, Trader):

    def __init__(self, node, rationale, **kw):
        ResourceAgent.__init__(self, node)
        Trader.__init__(self, rationale)
        self.trace = Tracer(node)
        self.trace = self.trace.add('%-12s' % self)
        self.listen_process = None
        self.rejected = set()
        self.cancelled = set()

    def start(self):
        self.listen_process = ListenProcess(self)
        activate(self.listen_process, self.listen_process.listen())
  

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


