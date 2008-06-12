from SimPy.Simulation import *
from models import GridModel
from message import Message
from market import Quote, Ask, Bid, MarketRules
from traders import ZIC, ZIP
from stats import dists
from trace import Tracer


class MessageWithQuote(Message):
    def __init__(self, quote, *a, **kw):
        super(MessageWithQuote, self).__init__(*a, **kw)
        self.quote = quote

class Advert(MessageWithQuote):
    """Advert sent to seller"""
    def process(self, src, dst, trace, **kw):
        if trace:
            trace("signalling seller that advert has arrived")
        dst.seller.receive_advert(self.quote)
        reactivate(dst.seller)

class PrivateQuote(MessageWithQuote):
    """quote sent to buyer"""
    def process(self, src, dst, trace, **kw):
        b = self.quote.buyer
        dst.confirm_buyer(b)
        if b.trace:
            b.trace("got %s" % self.quote.str(b))
        b.receive_quote(self.quote)

class Accept(MessageWithQuote):
    """Accept sent to seller"""
    def process(self, src, dst, trace, **kw):
        dst.seller.accept(self.quote)

class Reject(MessageWithQuote):
    """Rejection of acceptance, sent to buyer"""
    def process(self, src, dst, trace, **kw):
        dst.confirm_buyer(self.quote.buyer)
        self.quote.buyer.reject(self.quote)
        reactivate(self.quote.buyer)

class Confirm(MessageWithQuote):
    """Confirmation of acceptance, sent to buyer"""
    def process(self, src, dst, trace, **kw):
        dst.confirm_buyer(self.quote.buyer)
        self.quote.buyer.confirm(self.quote)
        reactivate(self.quote.buyer)

class Cancel(MessageWithQuote):
    """Cancellation of previous accept message, sent to seller"""
    def process(self, src, dst, trace, **kw):
        dst.seller.cancel(self.quote)


class Buyer(Process):
    pass

class Seller(Process):
    pass

class SBBuyer(Buyer):
    def __init__(self, id, node, timeout):
        super(SBBuyer, self).__init__("SBBuyer %d" % id)
        self.id = id
        self.node = node
        self.timeout = timeout
        self.quotes = []

    @property
    def valid_quotes(self):
        return (q for q in self.quotes if q.price < self.rational.limit)

    # signalling methods
    def receive_quote(self, quote):
        self.quotes.append(quote)

    def confirm(self, quote):
        self.confirmed = quote
 
    def reject(self, quote):
        self.rejected = quote

    def trade(self, job):
        self.trace = trace = Tracer(self.node).add('sbb%-5d' % self.id).add('j%-5d' % job.id)

        adverts = 0
        quote = Bid(self, None, job, None)
        advert = Advert(quote)
        self.confirmed = False
        self.rejected = False
        if trace:
            trace("new buyer shouting to %d nodes" % len(self.node.neighbors))
        self.node.shout_msg(advert)

        # fixed timeout - we always want to wait this long
        yield hold, self, self.timeout 
        if trace:
            trace("buyer timed out")

        timedout = []
        while self.quotes:
            self.rejected = self.confirmed = False

            # resort as we may have got other quotes
            self.quotes.sort(key=lambda q: q.price)
            if trace:
                trace("have %d quotes" % len(self.quotes))

            self.quote = self.quotes.pop(0) # cheapest quote

            accept = Accept(self.quote)
            accept.send_msg(self.node, self.quote.seller.node)
            if trace:
                trace("accepting best ask: %s" % self.quote.str(self))

            target_time = now() + self.timeout
            next_quote = False

            while self.quote: # quote still valid

                # this can be interupted
                yield hold, self, target_time - now()

                if self.confirmed: # received confirm message
                    if self.confirmed == self.quote: # current quote confirmed
                        if trace: 
                            trace("accept confirmed")
                        #self.record_trade(self.confirmed)
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

        if trace: trace("run out of quotes")
        #TODO: report failure
        raise StopIteration

    def __str__(self):
        return "SBBuyer %d" % self.id

class SBSeller(Seller):

    def __init__(self, id, node, timeout, rationale, *a, **kw):
        super(SBSeller, self).__init__("SBSeller %d" % id)
        self.id = id
        self.node = node
        self.timeout = timeout
        self.rationale = rationale
        self.active_trades = {}
        self.advert = None
        self.quoted_jobs = set()
    
    @property
    def resource(self): return self.node.resource

    def trade(self):
        self.trace = Tracer(self.node).add('sbs%-5s' % self.id)
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
                        price = self.rationale.quote()
                        quote = Ask(ad.buyer, self, job, price)
                        private = PrivateQuote(quote)
                        private.send_msg(self.node, quote.buyer.node)
                        self.quoted_jobs.add(job.id)
                        if trace:
                            trace("sending offer %s" % quote)

                        # spawn process to handle rest of the process
                        process = self.TradeProcess()
                        activate(process, process.trade(self, quote, trace))
                        self.active_trades[job] = process
                    else:
                        if trace:
                            trace("resource has no room for job")
                else:
                    if trace: 
                        trace("WARNING: received advert for job already trading for")
            else:
                if self.trace:
                    self.trace("WARNING: woken up for unkown reason")
            self.advert = None
                            

    # signalling methods
    def receive_advert(self, quote):
        self.advert = quote

    def accept(self, quote):
        trace = self.trace.add('j%-5s' % quote.job.id)
        if quote.job in self.active_trades:
            p = self.active_trades[quote.job]
            p.receive_accept(quote)
            reactivate(p)
        elif quote.job.id in self.quoted_jobs:
            if trace:
                trace("got an accept for a job we've timed out on")
        elif trace:
            trace("WARNING: got an accept for a job we didn't quote on")

    def cancel(self, quote):
        trace = self.trace.add('j%-5s' % quote.job.id)
        if quote.job in self.active_trades:
            p = self.active_trades[quote.job]
            p.receive_cancel(quote)
            reactivate(p)
        elif quote.job in self.resource.jobs:
            self.node.resource.cancel(quote.job)
            trace("Got cancel for job already started, cancelling")
            #TODO: calculate wasted time?
        elif quote.job.id in self.quoted_jobs:
            trace("got a cancel for a timed out job")
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
                assert self.accept == quote
                if seller.resource.can_allocate(quote.job): # can we still do it?
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
                assert self.cancel == quote
                if quote.job in seller.resource.jobs:
                    trace("got pre-timeout cancel, terminating job and bidding")
                    seller.resource.cancel(quote.job)
                else:
                    trace("got cancel before we got an accept!")
                    # SimPy work around
                    #canceller = Process()
                    #canceller.cancel(self)

            else: # we've timed out
                if trace:
                    trace("timed out waiting for response to offer")

            del seller.active_trades[job]

        def receive_accept(self, quote):
            self.accept = quote

        def receive_cancel(self, quote):
            self.cancel = quote



def setup(graph):
    rules = MarketRules()
    rules.min = 1
    rules.max = 1000
    limits = dists.uniform(50, 150)
    for n in graph.nodes_iter():
        n.seller = SBSeller(n.id, n, 120, ZIC(False, int(limits()), rules))


class SBModel(GridModel):
    def new_process(self):
        dst = self.random_node()
        job = self.new_job()
        buyer = SBBuyer(job.id, dst, 10)
        dst.buyers.add(buyer)
        return buyer, buyer.trade(job)




