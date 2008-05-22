import math
import operator

def normalise_price(p):
    # normalise to 2dp
    return math.floor((p * 100)+ 0.5) / 100


class Quote(object):
    """A quote in the market"""
    def __init__(self, bid, job, price):
        self.job = job
        self.bid = bid
        self.ask = not bid
        self.price = price
        self.quantity = job.amount


def Bid(job, price):
    """Factory for a Bid quote"""
    return Quote(True, job, price)

def Ask(job, price):
    """Factory for an Ask quote"""
    return Quote(False, job, price)

class Trade(object):
    """Record of a trade"""
    def __init__(self, buyer, seller, price, quote, time):
        pass

class MarketRules(object):
    pass

class Trader(object):
    def __init__(self, buyer, limit, rules):
        self.buyer = buyer
        self.seller = not buyer
        
        self.limit = limit  # limit price
        self.market = rules  # market rules

        # valid bids
        self.seller_range = (limit, self.market.max)
        self.buyer_range = (self.market.min, limit)

    # stub methods
    def observe(self, quote):
        pass

    def quote(self):
        pass

# factory functions for traders
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
        self.coeff = (1.0 - self.momentum) * self.learning_rate
        
        super(ZIP, self).__init__(*a, **kw)

        self.last_change = 0;
        self.profit = self.buyer and -0.1 or 0.1
        self.lower_margin = self.buyer and 1.1 or 0.9
        self.raise_margin = self.buyer and 0.9 or 1.1

    @property
    def price(self):
        return self.limit * (1 + self.profit)
        

    def update_profit(self, target):
        """Updates the profit margin using the Widrow-Hoff learning rule"""
        change = self.coeff * (target - self.price) + self.momentum * self.last_change
        self.last_change = change
        new_profit = ((self.price + change) / self.limit) - 1.0

        if self.buyer: 
            self.profit = new_profit < 0 and new_profit or 0
        else:
            self.profit = new_profit > 1 and new_profit or 0

    def observe(self, quote, success):
        change = 0

        if self.buyer:
            quote_is_better = self.price >= quote.price 
            competing_quote = quote.bid 
        else:
            quote_is_better = self.price <= quote.price
            competing_quote = quote.ask

        if success: # trade was succesful
            # if our price is worse than this, increase margin
            if quote_is_better:
                print "successful better quote: raise margin"
                change = self.raise_margin
            # if it's a quote we would not have won, lower margin
            elif not competing_quote:
                print "successful worse quote: lower margin"
                change = self.lower_margin
        else: # no deal
            # if it's a competing quote and we're worse, lower margin
            if competing_quote and quote_is_better:
                print "unsuccessful better competing quote: lower margin"
                change = self.lower_margin

        if (change != 0):
            self.update_price(self.price * change)


    def quote(self):
        pass



