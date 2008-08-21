from SimPy.Simulation import activate, hold, passivate, reactivate, now, Process
from util import reactivate_on_call, RingBuffer
from sbmarket import Ask, Seller
import record
from trace import Tracer
from messages import *


class SBSeller(Seller):

    def __init__(self, id, rationale, node, timeout, *a, **kw):
        super(SBSeller, self).__init__(id, rationale, node)
        self.timeout = timeout
        self.active_trades = {}
        self.advert = None
        self.quoted_jobs = RingBuffer(500)
        self.cancelled_ids = set()
        self.trace.add('sbs%-5s' % self.id)
    
    @property
    def resource(self): return self.node.resource

    def trade(self):
        while 1:
            yield passivate, self
            if self.advert:
                ad = self.advert
                job = ad.job
                trace = self.trace.add('j%-5s' % job.id)
                if trace: 
                    trace("advert from %s at %s" % (ad.buyer, ad.buyer.node))

                if job not in self.active_trades:
                    if self.resource.can_allocate(job):

                        # generate a quote and send it
                        price = self.rationale.quote()
                        quote = Ask(ad.buyer, self, job, price)
                        private = PrivateQuote(quote)
                        private.send_msg(self.node, quote.buyer.node)
                        
                        self.quoted_jobs.append(job.id)
                        if trace:
                            trace("sending offer %s" % quote)

                        # spawn process to handle rest of the process
                        process = self.TradeProcess()
                        activate(process, process.trade(self, quote, trace))
                        self.active_trades[job] = process
                    else:
                        record.record_failure_reason(job.id, "Too Busy")
                        if trace:
                            trace("resource has no room for job")
                else:
                    trace and trace("WARNING: received advert for job already trading for")
            else:
                self.trace("WARNING: woken up for unkown reason, no advert")
            self.advert = None
                            

    # signalling methods

    # called by Advert
    @reactivate_on_call
    def receive_advert(self, quote):
        self.advert = quote

    # Called by Accept
    def accept(self, quote):
        trace = self.trace.add('j%-5s' % quote.job.id)

        # record sucessful quote
        self.rationale.observe(quote, True)

        # manage quote
        if quote.job in self.active_trades:
            p = self.active_trades[quote.job]
            p.receive_accept(quote)
        elif quote.job.id in self.quoted_jobs:
            if trace:
                trace("got an accept for a job we've timed out on")
        elif trace:
            trace("WARNING: got an accept for a job we didn't quote on")

    # Called by cancel
    def cancel(self, quote):
        trace = self.trace.add('j%-5s' % quote.job.id)
        if quote.job in self.active_trades:
            p = self.active_trades[quote.job]
            p.receive_cancel(quote)
        elif quote.job.id in self.cancelled_ids:
            trace("WARNING: got cancel for job already cancelled")
        elif quote.job in self.resource.jobs:
            self.node.resource.cancel(quote.job)
            if trace: trace("Got cancel for job already started, cancelling")
            #TODO: calculate wasted time?
        elif quote.job.id in self.quoted_jobs:
            if trace: trace("got a cancel for a timed out job")
        elif trace: 
            trace("WARNING: got a cancel for a unknown job")

    def __str__(self):
        return "SBSeller %d" % self.id


    class TradeProcess(Process):
        """Sub process to manage each active quote"""
        def trade(self, seller, quote, trace):
            job = quote.job
            self.accept = None
            self.cancel = None
            
            yield hold, self, seller.timeout

            if self.accept: # we've received an accept
                if self.accept != quote:
                    trace("WARNING: got accept for other quote!")
                    print quote, self.accept
                else:
                    # record successful quote
                    seller.rationale.observe(quote, True)
                    
                    # can we still do it?
                    if seller.resource.can_allocate(quote.job): 
                        if trace:
                            trace("got accept, sending confirm")
                        confirm = Confirm(quote)
                        confirm.send_msg(seller.node, quote.buyer.node)
                        seller.resource.start(quote.job)
                        #TODO yield duration of job here?

                    else: # we cannot honour our original quote
                        if trace:
                            trace("got accept, now too busy, rejecting")
                        reject = Reject(quote)
                        reject.send_msg(seller.node, quote.buyer.node)

            elif self.cancel: # we've received a cancel
                if quote.job in seller.resource.jobs:
                    trace and trace("got pre-timeout cancel, terminating job and bidding")
                    seller.resource.cancel(quote.job)
                    seller.cancelled_ids.add(quote.job.id)
                else:
                    if trace:
                        trace("WARNING: got cancel before we got an accept!")

            else: # we've timed out

                #record unsucessful quote
                seller.rationale.observe(quote, False)

                if trace:
                    trace("timed out waiting for response to offer")

            # clean up job record
            del seller.active_trades[job]

        @reactivate_on_call
        def receive_accept(self, quote):
            self.accept = quote

        @reactivate_on_call
        def receive_cancel(self, quote):
            self.cancel = quote



