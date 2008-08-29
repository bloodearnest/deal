from SimPy.Simulation import reactivate
from message import MessageWithQuote
import record

# listen process messages
class Advert(MessageWithQuote):
    """Advert sent to seller"""
    def process(self, src, dst, trace, **kw):
        self.record(dst)
        # pass it on 
        ttl = kw.get('ttl', 1)
        dst.shout_msg(self, ttl=ttl)
        dst.seller.quote(self.quote)


class PrivateQuote(MessageWithQuote):
    """quote sent to buyer"""
    def process(self, src, dst, trace, **kw):
        buyer = self.check_buyer(dst, trace)
        if buyer and buyer.active:
            buyer.quote(self.quote)

class Accept(MessageWithQuote):
    """Accept sent to seller"""
    def process(self, src, dst, trace, **kw):
        dst.seller.accept(self.quote)

# accept process messages

class Reject(MessageWithQuote):
    """Rejection of acceptance, sent to buyer"""
    def process(self, src, dst, trace, **kw):
        buyer = self.check_buyer(dst, trace)
        if buyer and buyer.active:
            buyer.reject(self.quote)

class Confirm(MessageWithQuote):
    """Confirmation of acceptance, sent to buyer"""
    def process(self, src, dst, trace, **kw):
        buyer = self.check_buyer(dst, trace)
        if buyer and buyer.active:
            buyer.confirm(self.quote)

# confirm process
class Cancel(MessageWithQuote):
    """Cancellation of previous accept message, sent to seller"""
    def process(self, src, dst, trace, **kw):
        dst.seller.cancel(self.quote)

