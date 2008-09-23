from SimPy.Simulation import now
from trace import Tracer
from processes import *
from trader import Trader
from agents import ResourceAgent


class Seller(ResourceAgent, Trader):

    def __init__(self, node, rationale, **kw):
        ResourceAgent.__init__(self, node)
        Trader.__init__(self, rationale, **kw)
        self.trace = Tracer(node)
        self.trace = self.trace.add('%-12s' % self)
        self.listen_process = None
        self.quote_timeouts = dict()

    def start(self):
        self.listen_process = ListenProcess(self)
        activate(self.listen_process, self.listen_process.listen())
  

    def set_quote_timeout(self, quote, trace):
        trace and trace("setting rationale timeout %s" % (id, ))
        p = RationaleTimeout()
        p.start(p.timeout(self, quote.id, quote, self.quote_timeout, trace))
        self.quote_timeouts[quote.id] = p

    def cancel_quote_timeout(self, id, trace):
        if id in self.quote_timeouts:
            trace and trace("cancelling rationale timeout %s" % (id, ))
            process = self.quote_timeouts[id]
            cancel_process(process)
            del self.quote_timeouts[id]
        elif id in self.timedout:
            trace and trace("rationale timeout already fired %s" % (id, ))
        elif trace:
            trace("WARNING: unknown quote timeout cancelled %s" % (id, ))

    def process_quote_timeout(self, id, quote, trace):
        if id in self.quote_timeouts:
            trace and trace("observing failed quote %s" % (id, ))
            self.rationale.observe(quote, False)
            self.timedout.add(id)
            del self.quote_timeouts[id]
        elif id in self.timedout:
            trace("WARNING: quote timeout already timed out %s" % (id, ))
        else:
            trace("WARNING: unknown quote timeout firing %s" % (id, ))


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


