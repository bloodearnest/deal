from SimPy.Simulation import activate, hold, passivate, reactivate, now, Process
from util import reactivate_on_call, RingBuffer
from record import ecorecord as record
from market import Ask
from traders.seller import Seller
from traders.processes import *
from trace import Tracer
from messages import *


class SBSeller(Seller):

    def __init__(self, node, rationale,  **kw):
        super(SBSeller, self).__init__(node, rationale, **kw)
        self.offers = RingBuffer(500)

    # internal ListenProcess interface
    def quote_received(self, quote):
        trace = self.trace.add('j%-5s' % quote.job.id)
        trace and trace("advert from %s at %s" % (quote.buyer, quote.buyer.node))
        
        if quote not in self.offers:
            if self.resource.can_allocate(quote.job):

                # generate a quote and send it
                self.price = self.rationale.quote()
                quote = Ask(quote.buyer, self, quote.job, self.price)
                private = PrivateQuote(quote)
                private.send_msg(self.node, quote.buyer.node)
                self.set_quote_timeout(quote, trace)

                self.offers.add(quote)
                trace and trace("sending offer %s" % quote)

            else:
                # TODO: add this record to the job object
                record.record_failure_reason(quote.job.id, "Too Busy")
                trace and trace("resource has no room for job")
                self.nrejected += 1
        else:
            trace("WARNING: received advert for job already trading for")


    def accept_received(self, quote):
        trace = self.trace.add('j%-5s' % quote.job.id)

        if quote in self.offers:
            # we know this one
            trace and trace("got accept from %s" % quote.buyer)
            
            self.cancel_quote_timeout(quote.id, trace)
            self.rationale.observe(quote, True)

            # can we still do it?
            if self.resource.can_allocate(quote.job): 
                self.confirm_and_start_job(
                        quote.job, quote.buyer, quote)
                
            else: # we cannot honour our original quote
                trace and trace("got accept, now too busy, rejecting")
                record.record_failure_reason(quote.job.id, "Too Busy Later")
                self.send_reject(quote.buyer, quote)
                self.nrejected += 1

        else: 
            trace and trace("got an accept for a job we've timed out on")


    # diable confirm/reject as in sealedbid these are buyer only
    confirm = Seller.disable("confirm")
    reject = Seller.disable("reject")

    def quote_timedout(self):
        """this is for a regular pulse timeout"""
        pass
        #self.rationale.observe(Ask(None, self, None, self.price), False)




