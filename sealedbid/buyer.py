from SimPy.Simulation import activate, reactivate, now, hold, Process
from trace import Tracer
from record import ecorecord as record

from market import Bid
from messages import *
from traders.buyer import Buyer
from traders.processes import *

class SBBuyer(Buyer):
    def __init__(self, job, rationale, ttl=2, **kw):
        super(SBBuyer, self).__init__(job, rationale, **kw)
        self.ttl = ttl
        self.has_timedout = False
        self.valid_quotes = []
        self.ninvalid_quotes = 0
        self.have_received_quote = False

    def start(self):
        super(SBBuyer, self).start()
        self.has_timedout = False
        self.current_quote = self.advertise()

    def advertise(self):
        # initial advert and quote
        # TODO: add a initial buyer quoted price?
        quote = Bid(self, None, self.job, None)
        advert = Advert(quote)
        
        # send to self
        self.trace and self.trace("buyer sending to self")
        advert.send_msg(self.node, self.node, ttl=0)
        
        # send to others
        self.trace and self.trace("buyer shouting to %d nodes, ttl %s" 
                % (self.node.degree, self.ttl))
        self.node.shout_msg(advert, ttl=self.ttl)
        return quote

    # internal ListenProcess interface
    def quote_received(self, quote):
        if quote.price <= self.limit:
            self.valid_quotes.append(quote)
        else:
            self.ninvalid_quotes += 1
            
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
            self.start_accept_process(
                    self.current_quote.seller, 
                    self.current_quote, 
                    self.accept_timeout)
            
            self.trace and self.trace("accepting best ask: %s" 
                    % self.current_quote.str(self))
            
            self.accepted.add(self.current_quote)

        else:
            self.trace and self.trace("no valid quotes")

            if self.migrations < 5:
                self.migrations += 1
                self.migrate()
            else:
                self.trace and self.trace("no more migrations allowed!")
                self.record_failure()
                self.finish_trading()
                self.cancel_all()

    #internal AcceptProcess interface
    def confirm_received(self, confirm):
        if confirm == self.current_quote: # current quote confirmed
            self.trace and self.trace("accept confirmed")
            self.record_success(confirm)
            self.finish_trading()
            self.cancel_all()
            self.accept_process = None

        elif confirm.id in self.timedout: # old quote confirms
            self.trace and self.trace("got confirm from timed out quote")
            # TODO: may want to go with this confirm instead, as it
            # was probably better than the current one
        else: # unknown confirm
            self.trace("WARNING: got random confirm: %s" 
                    % confirm.str(self))

    def reject_received(self, reject):
        if reject == self.current_quote: # current quote rejected
            self.trace and self.trace("accept rejected, choosing next quote")
            self.nrejected += 1
            self.current_quote = None
            self.accept_process = None

            # move onto next quote
            self.accept_best_quote()

        elif reject.id in self.timedout:
            self.trace and self.trace("accept rejected, but had already timed out")
        else:
            self.trace("WARNING: got reject for unknown quote: %s" 
                    % reject.str(self))
   

    def accept_timedout(self, accept):
        self.trace and self.trace(" accept timed out, sending cancel")
        cancel = Cancel(self, self.current_quote.seller, accept)
        cancel.send_msg(self.node, accept.seller.node)
        self.timedout.add(self.current_quote.id)
        record.record_failure_reason(accept.job.id, "Timedout")
        self.current_quote = None
        self.accept_process = None
        self.accept_best_quote()



    def record_failure(self):
        if (self.nrejected + len(self.timedout) == 0 and 
                self.ninvalid_quotes > 0):
            record.record_failure_reason(self.job.id, "High Buyer Limit")
        quote = Bid(self, None, self.job, self.price)
        record.record_failure(self, quote)

    def record_success(self, quote):
        record.record_success(self, quote)







