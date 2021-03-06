from trace import BaseTracer

class Trader(object):
    def __init__(self, rationale, quote_timeout, accept_timeout):
        self.rationale = rationale
        self.active = True
        self.price = self.rationale.quote()
        self.regions = set()
        self.quote_timeout = quote_timeout
        self.accept_timeout = accept_timeout
    
    @property
    def limit(self):
        return self.rationale.limit
    
    def __str__(self):
        return "%s %d" % (self.__class__.__name__, self.id)

    @staticmethod
    def disable(name):
        def _disable(self, quote):
            self.trace("WARNING: %s got an %s: %s" % (self, name, accept.str(self)))

    # all traders get quotes
    # public ListentProcess message interface
    def quote(self, quote):
        self.listen_process.signal("quote", quote)

    def accept(self, accept):
        self.listen_process.signal("accept", accept)

