from SimPy.Simulation import activate, reactivate, now, hold
from util import reactivate_on_call
from market import Bid,  Buyer
from trace import Tracer
from record import record_trade

from messages import *

class SBBuyer(Buyer):
    def __init__(self, id, node, timeout, rationale):
        super(SBBuyer, self).__init__("SBBuyer %d" % id)
        self.id = id
        self.node = node
        self.timeout = timeout
        self.rationale = rationale
        self.valid_quotes = []
        self.invalid_quotes = []


    def trade(self, job):
        """The Buyers PEM"""
        self.trace = trace = Tracer(self.node).add('sbb%-5d' % self.id).add('j%-5d' % job.id)

        adverts = 0

        # initial advert and quote
        # TODO: add a initial buyer quoted price?
        quote = Bid(self, None, job, None)
        advert = Advert(quote)

        if trace:
            trace("new buyer shouting to %d nodes" % len(self.node.neighbors))
        self.node.shout_msg(advert)

        # fixed timeout - we should always want to wait this long
        yield hold, self, self.timeout 
        if trace:
            trace("buyer timed out")

        # store quotes that have timed out
        timedout = []

        while self.valid_quotes: # list of valid
            self.rejected = self.confirmed = False

            # sort quotes (we may have got other quotes in the mean time)
            self.valid_quotes.sort(key=lambda q: q.price)
            if trace:
                trace("have %d quotes" % len(self.quotes))

            self.quote = self.valid_quotes.pop(0) # cheapest quote

            # accept the cheapest quote
            accept = Accept(self.quote)
            accept.send_msg(self.node, self.quote.seller.node)
            if trace:
                trace("accepting best ask: %s" % self.quote.str(self))

            # store our maximum time out
            target_time = now() + self.timeout

            while self.quote: # quote still valid

                # this can be interupted
                yield hold, self, target_time - now()

                if self.confirmed: # received confirm message
                    if self.confirmed == self.quote: # current quote confirmed
                        if trace: 
                            trace("accept confirmed")
                        record_trade(self.confirmed, True)

                        raise StopIteration # we are done!

                    elif self.confirmed in timedout: # old quote confirms
                        if trace:
                            trace("got confirm from timed out quote")
                        # TODO: may want to go with this confirm instead, as it
                        # was probably better than the current one
                    elif trace: # unknown confirm
                        trace("WARNING: got random confirm: %s" 
                                % self.confirmed.str(self))
                    self.confirmed = False

                elif self.rejected: # got a rejection message
                    if self.rejected == self.quote: # current quote rejected
                        if trace:
                            trace("accept rejected, choosing next quote")
                        self.quote = None
                    elif self.rejected in timedout:
                        # reject from quote already timed out
                        if trace: 
                            trace("accept rejected, but had already timed out")
                    elif trace:
                        trace("WARNIG: got reject for unknown quote: %s" %
                                self.rejected.str(self))
                    self.rejected = False

                else: # timed out
                    if trace:
                        trace("timed out, sending cancel")
                    cancel = Cancel(self.quote)
                    cancel.send_msg(self.node, self.quote.seller.node)
                    timedout.append(self.quote)
                    self.quote = None

        if trace: trace("run out of valid quotes")
        
        #TODO: report failure
        record_trade(quote, False)

        raise StopIteration

    # signalling methods called by messages

    def receive_quote(self, quote):
        if quote.price <= self.rationale.limit:
            self.valid_quotes.append(quote)
        else:
            self.invalid_quotes.append(quote)

    # called by confirm message
    @reactivate_on_call
    def confirm(self, quote):
        """Mark a quote as confirmed and reactivate"""
        self.confirmed = quote
 
    # called by reject message
    @reactivate_on_call
    def reject(self, quote):
        """Mark a quote as rejected acn reactivate"""
        self.rejected = quote

    def __str__(self):
        return "SBBuyer %d" % self.id


