from SimPy.Simulation import activate, reactivate, now, hold
from util import reactivate_on_call
from sbmarket import Bid,  Buyer
from trace import Tracer
import record

from messages import *

class SBBuyer(Buyer):
    def __init__(self, id, rationale, job, timeout, ttl=2):
        super(SBBuyer, self).__init__(id, rationale, job)
        self.timeout = timeout
        self.valid_quotes = []
        self.invalid_quotes = []
        self.have_received_quote = False
        self.ttl = ttl


    def trade(self):
        """The Buyers PEM"""
        job = self.job
        self.trace = trace = Tracer(self.node).add('sbb%-5d' % self.id).add('j%-5d' % job.id)

        # initial advert and quote
        # TODO: add a initial buyer quoted price?
        quote = Bid(self, None, job, None)
        advert = Advert(quote)

        if trace:
            trace("new buyer shouting to %d nodes, ttl %s" 
                    % (len(self.node.neighbors), self.ttl))
        self.node.shout_msg(advert, ttl=self.ttl)

        tstart = now()
        yield hold, self, self.timeout 
        while self.have_received_quote:
            self.have_received_quote = False
            if trace:
                trace("buyer time out reset")
            yield hold, self, self.timeout
            
        if trace:
            trace("buyer timed out")
        record.buyer_timeouts.observe(now() - tstart)

        # store quotes that have timed out
        timedout = []
        rejected = []

        while self.valid_quotes: # list of valid
            self.rejected = self.confirmed = False

            # sort quotes (we may have got other quotes in the mean time)
            self.valid_quotes.sort(key=lambda q: q.price)
            if trace:
                trace("have %d quotes" % len(self.valid_quotes))

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
                        record.record_trade(self.confirmed, True)

                        raise StopIteration # we are done!

                    elif self.confirmed in timedout: # old quote confirms
                        if trace:
                            trace("got confirm from timed out quote")
                        # TODO: may want to go with this confirm instead, as it
                        # was probably better than the current one
                    else: # unknown confirm
                        trace("WARNING: got random confirm: %s" 
                                % self.confirmed.str(self))
                    self.confirmed = False

                elif self.rejected: # got a rejection message
                    if self.rejected == self.quote: # current quote rejected
                        if trace:
                            trace("accept rejected, choosing next quote")
                        rejected.append(self.quote.job.id)
                        record.record_failure_reason(job.id, "Too Busy Later")
                        self.quote = None
                    elif self.rejected in timedout:
                        # reject from quote already timed out
                        if trace: 
                            trace("accept rejected, but had already timed out")
                    elif trace:
                        trace("WARNING: got reject for unknown quote: %s" %
                                self.rejected.str(self))
                    self.rejected = False

                else: # timed out
                    if trace:
                        trace("timed out, sending cancel")
                    cancel = Cancel(self.quote)
                    cancel.send_msg(self.node, self.quote.seller.node)
                    timedout.append(self.quote)
                    record.record_failure_reason(job.id, "Timedout")
                    self.quote = None

        if trace: trace("run out of valid quotes")
 
        if len(rejected) + len(timedout) == 0 and len(self.invalid_quotes) > 0:
            record.record_failure_reason(job.id, "High Buyer Limit")

        record.record_failure(quote)

        self.finish_trading()
        raise StopIteration

    # signalling methods called by messages

    # called by PrivateQuote
    @reactivate_on_call
    def receive_quote(self, quote):
        if quote.price <= self.rationale.limit:
            self.valid_quotes.append(quote)
        else:
            self.invalid_quotes.append(quote)
        self.have_received_quote = True

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


