from SimPy.Simulation import reactivate
from message import MessageWithQuote

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

