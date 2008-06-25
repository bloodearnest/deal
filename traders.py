import random
from market import normalise_price

class Rationale(object):
    def __init__(self, buyer, limit, rules):
        self.buyer = buyer
        self.seller = not buyer
        
        self.limit = limit  # limit price
        self.market = rules  # market rules

        # valid bids
        self.seller_range = (limit, self.market.max)
        self.buyer_range = (self.market.min, limit)

    # stub methods
    def observe(self, quote, success):
        pass

    def quote(self, *a, **kw):
        pass


class ZIC(Rationale):
    def quote(self, *a, **kw):
        lower = upper = None
        if self.buyer:
            lower, upper = self.buyer_range
        else:
            lower, upper = self.seller_range

        r = random.random()
        return r * (upper - lower) + lower

class ZIP(Rationale):
    def __init__(self, *a, **kw):

        self.learning_rate = kw.pop('rate', 0.2)
        self.momentum = kw.pop('momentum', 0.3)
        self.coeff = (1.0 - self.momentum) * self.learning_rate
        
        super(ZIP, self).__init__(*a, **kw)

        self.last_change = 0;
        self.profit = self.buyer and -0.1 or 0.1
        self.lower_margin = self.buyer and 1.2 or 0.8
        self.raise_margin = self.buyer and 0.8 or 1.2

    @property
    def price(self):
        return normalise_price(self.limit * (1 + self.profit))
        
    def update_profit(self, target):
        """Updates the profit margin using the Widrow-Hoff learning rule"""
        change = (self.coeff * (target - self.price) +
                  self.momentum * self.last_change)
        self.last_change = change
        new_profit = ((self.price + change) / self.limit) - 1.0

        if self.buyer: 
            self.profit = new_profit < 0 and new_profit or 0
        else:
            self.profit = new_profit > 0 and new_profit or 0

    def observe(self, quote, success):
        change = 0

        if self.buyer:
            quote_is_better = self.price >= quote.price 
            competing_quote = quote.bid 
        else: # seller
            quote_is_better = self.price <= quote.price
            competing_quote = quote.ask

        if success: # trade was succesful
            # if our price is worse than this, increase margin
            if quote_is_better:
                #print "successful better quote: raise margin"
                change = self.raise_margin
            # if it's a quote we would not have won, lower margin
            elif not competing_quote:
                #print "successful worse quote: lower margin"
                change = self.lower_margin
        else: # no deal
            # if it's a competing quote and we're worse, lower margin
            if competing_quote and quote_is_better:
                #print "unsuccessful better competing quote: lower margin"
                change = self.lower_margin

        if change != 0:
            self.update_profit(self.price * change)


    def quote(self, *a, **kw):
        return self.price



