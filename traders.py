
class Trader(object):

    def __init__(self, limit):
        self.limit = limit

    def observe(self, quote):
        pass

    def quote(self):
        pass

    @property
    def utility(self):
        pass


class ZI(Trader):
    def quote(self):
        if self.buyer:
            return random.randint(market_minimum, self.limit)
        else
            return random.randint(self.limit, market_maximum)
