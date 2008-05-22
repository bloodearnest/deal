import traders
import message

class Quote(Message):

    def process(self, src, dst, log, **kw):
        quote = kw.pop('quote')

        dst.seller.observe(quote)

        for (buyer in dst.buyers)
            buyer.observe(quote)

        



