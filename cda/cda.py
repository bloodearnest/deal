from SimPy.Simulation import *

class CDATrader(Process):

    def observe(self, quote):
        acceptable = self.rationale.observe(quote)
        if acceptable:
            accept = Accept(quote)
            accept.send_msg(self.node, quote.src)


class CDABuyer(CDATrader):
    def __init__(self, *a, **kw):
        self.job = kw.pop('job')
        self.sold = False
        super(CDABuyer, self).__init__(*a, **kw)

    def trade(self):
        while still_trading():
            yield hold, self.period
            price = self.rationale.quote()
            quote = Bid(self.job, price)
            shout = Shout(quote)
            node.shout_msg(quote)




# CDA messages
class Shout(Message):
    def __init__(self, quote, *a, **kw)
        super(Message, self).__init__(*a, **kw)
        self.quote = quote

    def process(self, src, dst, log, **kw):
        if self.quote.bid:
            dst.seller.observe(self.quote)
        else: # asks
            for buyer in dst.buyers:
                buyer.observe(self.quote)

class Accept(Message):
    def process(self, src, dst, log, **kw):
        pass

class Confirm(Message):
    def process(self, src, dst, log, **kw):
        pass





