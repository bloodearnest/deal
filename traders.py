import math
import operator

class Quote(object):
    def __init__(self, bid, job, price):
        self.job = job
        self.bid = bid
        self.ask = not bid
        self.price = price
        self.quantity = job.amount

def Bid(job, price):
    return Quote(True, job, price)

def Ask(job, price):
    return Quote(False, job, price)



class Trader(object):
    def __init__(self, buyer, limit, min, max):
        self.buyer = buyer
        self.limit = limit
        self.market_min = min
        self.market_max = max
        self.seller_range = (limit, max)
        self.buyer_range = (min, limit)

    def observe(self, quote):
        pass

    def quote(self):
        pass

    @property
    def utility(self):
        pass

# factory functions
def Buyer(cls, *a, **kw):
    return cls(True, *a, **kw)

def Seller(cls, *a, **kw):
    return cls(False, *a, **kw)

# trader algorithms
class ZIC(Trader):
    def quote(self):
        return random.randint(self.buyer and self.buyer_range 
                                          or self.seller_range)


class ZIP(Trader):
    def __init__(self, *a, **kw):

        self.learning_rate = kw.pop('rate', 0.2)
        self.momentum = kw.pop('momentum', 0.3)

        super(ZIP, self).__init__(*a, **kw)

        self.last_change = 0;
        self.profit = self.buyer and -0.1 or 0.1
        self.price = (self.market_max - self.market_min) / 2
        self.coeff = (1.0 - self.momentum) * self.learning_rate
        self.lower_margin = self.buyer and 1.1 or 0.9
        self.raise_margin = self.buyer and 0.9 or 1.1

    def update_price(self, target):
        # Widrow-Hoff learning rule, a la Cliff 97
        change = self.coeff * (target - self.price) + self.momentum * self.last_change

        self.last_change = change

        new_profit = ((self.price + change) / self.limit) - 1.0

        if self.buyer: 
            self.profit = new_profit < 0 and new_profit or 0
        else:
            self.profit = new_profit > 1 and new_profit or 0

        self.price = self.limit * (1 + self.profit)

        # normalise to 1/100
        self.price = math.floor((self.price * 100)+ 0.5) / 100


    def observe(self, quote, success):
        margin_change = 0

        if self.buyer:
            quote_is_better = self.price >= quote.price 
            competing_quote = quote.bid 
        else:
            quote_is_better = self.price <= quote.price
            competing_quote = quote.ask

        if success:
            # if our price is worse than this, increase margin
            if quote_is_better:
                print "successful better quote: raise margin"
                margin_change = self.raise_margin
            # if it's a quote we would not have won, lower margin
            elif not competing_quote:
                print "successful worse quote: lower margin"
                margin_change = self.lower_margin
        else: # no deal
            # if it's a competing quote and we're worse, lower margin
            if competing_quote and quote_is_better:
                print "unsuccessful better competing quote: lower margin"
                margin_change = self.lower_margin

        if (margin_change != 0):
            self.update_price(self.price * margin_change)


    def quote(self):
        pass



