from SimPy.Simulation import activate, hold, passivate, reactivate, now, Process
from util import reactivate_on_call, RingBuffer
import record
from market import Ask
from traders.seller import Seller
from traders.processes import *
from trace import Tracer
from messages import *


class SBSeller(Seller):

    def __init__(self, id, rationale, node, **kw):
        super(SBSeller, self).__init__(id, rationale, node, **kw)
        self.offers = RingBuffer(500)
        self.cancelled_ids = set()
    
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
                
                self.offers.add(quote)
                trace and trace("sending offer %s" % quote)

            else:
                # TODO: add this record to the job object
                record.record_failure_reason(quote.job.id, "Too Busy")
                trace and trace("resource has no room for job")
                self.rejected.add(quote.id)
        else:
            trace("WARNING: received advert for job already trading for")


    def accept_received(self, quote):
        trace = self.trace.add('j%-5s' % quote.job.id)

        if quote in self.offers:
            # we know this one
            trace and trace("got accept from %s" % quote.buyer)
            self.rationale.observe(quote, True)

            # can we still do it?
            if self.resource.can_allocate(quote.job): 
                
                # sending confirmation message
                trace and trace("got accept, sending confirm")
                confirm = Confirm(quote)
                confirm.send_msg(self.node, quote.buyer.node)
                
                # start procsses tpo listen for cancellations
                confirm_process = ConfirmProcess(self, quote)
                activate(confirm_process, confirm_process.confirm())
                self.confirm_processes[quote.job.id] = confirm_process

                # start the job
                trace and trace("starting job %s, eta %s" % 
                        (quote.job.id, now() + quote.job.duration))
                self.resource.start(quote.job, confirm_process)

            else: # we cannot honour our original quote
                record.record_failure_reason(quote.job.id, "Too Busy Later")
                trace and trace("got accept, now too busy, rejecting")
                reject = Reject(quote)
                reject.send_msg(self.node, quote.buyer.node)
                self.rejected.add(quote.id)

        else: 
            trace and trace("got an accept for a job we've timed out on")


    # diable confirm/reject as in sealedbid these are buyer only
    confirm = Seller.disable("confirm")
    reject = Seller.disable("reject")

    def quote_timedout(self):
        pass
        #self.rationale.observe(self.price, False)

    #internal ConfirmProcess interface
    def cancel_received(self, cancel):
        trace = self.trace.add('j%-5s' % cancel.job.id)

        if cancel.job in self.resource.jobs:
            trace and trace("got cancel, cancelling job %s" 
                    % cancel.job.id)
            self.resource.cancel(cancel.job);
            del self.confirm_processes[cancel.job.id]
        else:
            trace("WARNING: got cancel for job not running (%s)"
                    % cancel.job.id)

    def complete_received(self, complete):
        trace = self.trace.add('j%-5s' % complete.job.id)
        trace and trace("job %s completed, cleaning up" 
                % complete.job.id)
        del self.confirm_processes[complete.job.id]




