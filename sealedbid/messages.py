from SimPy.Simulation import reactivate
from message import MessageWithQuote
import record

class Advert(MessageWithQuote):
    """Advert sent to seller"""
    def process(self, src, dst, trace, **kw):
        self.record(dst)
        ttl = kw.get('ttl', 1)
        dst.shout_msg(self, ttl=ttl)

        if trace:
            trace("signalling seller that advert has arrived")
        dst.seller.receive_advert(self.quote)

class PrivateQuote(MessageWithQuote):
    """quote sent to buyer"""
    def process(self, src, dst, trace, **kw):
        b = self.quote.buyer
        dst.confirm_buyer(b, trace)
        if b.active:
           b.trace and b.trace("got %s" % self.quote.str(b))
           b.receive_quote(self.quote)

class Accept(MessageWithQuote):
    """Accept sent to seller"""
    def process(self, src, dst, trace, **kw):
        dst.seller.accept(self.quote)

class Reject(MessageWithQuote):
    """Rejection of acceptance, sent to buyer"""
    def process(self, src, dst, trace, **kw):
        dst.confirm_buyer(self.quote.buyer, trace)
        if self.quote.buyer.active:
            self.quote.buyer.reject(self.quote)

class Confirm(MessageWithQuote):
    """Confirmation of acceptance, sent to buyer"""
    def process(self, src, dst, trace, **kw):
        dst.confirm_buyer(self.quote.buyer, trace)
        if self.quote.buyer.active:
            self.quote.buyer.confirm(self.quote)

class Cancel(MessageWithQuote):
    """Cancellation of previous accept message, sent to seller"""
    def process(self, src, dst, trace, **kw):
        dst.seller.cancel(self.quote)

