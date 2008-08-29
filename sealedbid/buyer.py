from SimPy.Simulation import activate, reactivate, now, hold, Process
from trace import Tracer
import record

from market import Bid
from messages import *
from traders.buyer import Buyer
from traders.processes import *

class SBBuyer(Buyer):
    def __init__(self, id, rationale, job, ttl=2, **kw):
        super(SBBuyer, self).__init__(id, rationale, job, **kw)
        self.ttl = ttl
        self.timedout = set()
        self.rejected = set()

        self.has_timedout = False

        self.valid_quotes = []
        self.invalid_quotes = []
        self.have_received_quote = False

    def start(self):
        super(SBBuyer, self).start()
        self.has_timeout = False
        self.current_quote = self.advertise()

    def advertise(self):
        # initial advert and quote
        # TODO: add a initial buyer quoted price?
        quote = Bid(self, None, self.job, None)
        advert = Advert(quote)
        self.trace and self.trace("buyer shouting to %d nodes, ttl %s" 
                % (self.node.degree, self.ttl))
        self.node.shout_msg(advert, ttl=self.ttl)
        return quote

    # internal ListenProcess interface
    def quote_received(self, quote):
        if quote.price <= self.limit:
            self.valid_quotes.append(quote)
        else:
            self.invalid_quotes.append(quote)
            
        self.trace and self.trace("got %s" % (quote.str(self)))
        self.trace and self.trace("buyer timeout reset")

    # diable accept, cancel, complete as in sealedbid they are seller only
    accept = Buyer.disable("accept")
    cancel = Buyer.disable("cancel")
    complete = Buyer.disable("complete")

    def quote_timedout(self):
        # only first time out triggers the bidding
        if not self.has_timedout:
            self.trace and self.trace("buyer timed out")
            record.buyer_timeouts.observe(now() - self.start_time)
            self.has_timedout = True
            self.accept_best_quote()


    def accept_best_quote(self):
        if self.accept_process:
           self.trace("WARNING: accept process already active")
        elif self.valid_quotes:
            
            # always resort quotes (we may have got other 
            # quotes in the mean time)
            self.valid_quotes.sort(key=lambda q: q.price)
            self.trace and self.trace("have %d valid quotes" 
                    % len(self.valid_quotes))

            # accept the cheapest quote
            self.current_quote = self.valid_quotes.pop(0)
            accept = Accept(self.current_quote)
            accept.send_msg(self.node, self.current_quote.seller.node)
            self.trace and self.trace("accepting best ask: %s" 
                    % self.current_quote.str(self))
            self.accepted.add(self.current_quote)

            # start accept process
            self.accept_process = AcceptProcess(self, self.current_quote)
            activate(self.accept_process, self.accept_process.accept())

        else:
            self.trace and self.trace("no valid quotes")

            if self.migrations < 5:
                self.migrations += 1
                self.migrate()
            else:
                self.trace and self.trace("no more migrations allowed!")
                if (len(self.rejected) + len(self.timedout) == 0 and 
                        len(self.invalid_quotes) > 0):
                    record.record_failure_reason(job.id, "High Buyer Limit")
                record.record_failure(quote)
                self.finish_trading()
                self.cancel_all()


    #internal AcceptProcess interface
    def confirm_received(self, confirm):
        if confirm == self.current_quote: # current quote confirmed
            self.trace and self.trace("accept confirmed")
            record.record_trade(confirm, True)
            self.finish_trading()
            self.cancel_all()
            self.accept_process = None

        elif confirm in self.timedout: # old quote confirms
            self.trace and self.trace("got confirm from timed out quote")
            # TODO: may want to go with this confirm instead, as it
            # was probably better than the current one
        else: # unknown confirm
            self.trace("WARNING: got random confirm: %s" 
                    % confirm.str(self))

    def reject_received(self, reject):
        if reject == self.current_quote: # current quote rejected
            self.trace and self.trace("accept rejected, choosing next quote")
            self.rejected.add(self.current_quote.job.id)
            record.record_failure_reason(reject.job.id, "Too Busy Later")
            self.current_quote = None
            self.accept_process = None

            # move onto next quote
            self.accept_best_quote()

        elif reject in self.timedout:
            self.trace and self.trace("accept rejected, but had already timed out")
        else:
            self.trace("WARNING: got reject for unknown quote: %s" 
                    % reject.str(buyer))
   

    def accept_timedout(self, accept):
        self.trace and self.trace(" accept timed out, sending cancel")
        cancel = Cancel(accept)
        cancel.send_msg(self.node, accept.seller.node)
        self.timedout.add(self.current_quote)
        record.record_failure_reason(accept.job.id, "Timedout")
        self.current_quote = None
        self.accept_process = None
        self.accept_best_quote()





