from trace import BaseTracer

class Trader(object):
    def __init__(self, id, rationale, **kw):
        self.id = id
        self.rationale = rationale
        self.active = True
        self.price = self.rationale.quote()
        self.regions = set()
        self.trace = BaseTracer()
        self.quote_timeout = kw.pop("quote_timeout", 5)
        self.accept_timeout = kw.pop("accept_timeout", 10)
    
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

    # public AcceptProcess message interface
    # handled differently by buyers/sellers, so disable in trader
    def confirm(self, confirm):
        self.trace("WARNING: %s got an confirm: %s" % (self, confirm.str(self)))

    def reject(self, reject):
        self.trace("WARNING: %s got an reject: %s" % (self, reject.str(self)))

    # public ConfirmProcess message interface
    # handled differently by buyers/sellers, so disable in trader
    def cancel(self, cancel):
        self.trace("WARNING: %s got an cancel: %s" % (self, cancel.str(self)))

    def complete(self, quote):
        self.trace("WARNING: %s got an complete: %s" % (self, quote.str(self)))

        
    # internal ListenProcess interface
    def quote_received(self, quote):
        pass
    
    def accept_received(self, quote):
        pass

    def quote_timedout(self):
        pass

    #internal AcceptProcess interface
    def confirm_received(self, confirm):
        pass

    def reject_received(self, reject):
        pass

    def accept_timedout(self, accept):
        pass

    #internal ConfirmProcess interface
    def cancel_received(self, cancel):
        pass

    def complete_received(self, complete):
        pass

