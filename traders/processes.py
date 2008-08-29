from SimPy.Simulation import *
from util import reactivate_on_call, SignalProcess
from market import Bid, Ask
from trace import Tracer
import record

# stoopid simpy workaround because you can't cancel the currently
# active process
class CancelProcess(Process):
    def pem(self, process):
        yield hold, self, 0.000000001
        self.cancel(process)

def cancel_process(process):
    p = CancelProcess()
    p.start(p.pem(process))
    process = None


class ListenProcess(SignalProcess):
    """This process recieves the quotes coming in from others"""
    def __init__(self, trader):
        super(ListenProcess, self).__init__(self.__class__.__name__)
        self.trader = trader

    def listen(self):
        while 1:
            yield hold, self, self.trader.quote_timeout
            
            # we've received a quote
            if self.have_signal("quote"):
                self.trader.quote_received(self.get_signal_value("quote"))
                
            # we received an accept
            elif self.have_signal("accept"):
                self.trader.accept_received(self.get_signal_value("accept"))

            else:
                self.trader.quote_timedout()


class AcceptProcess(SignalProcess):
    def __init__(self, trader, quote):
        super(AcceptProcess, self).__init__(self.__class__.__name__)
        self.trader = trader
        self.quote = quote

    def accept(self):
        yield hold, self, self.trader.accept_timeout

        # we have a confirmed accept
        if self.have_signal("confirm"):
            self.trader.confirm_received(self.get_signal_value("confirm"))

        elif self.have_signal("reject"):
            self.trader.reject_received(self.get_signal_value("reject"))

        # we have timed out on accept
        else:
            self.trader.accept_timedout(self.quote)


class ConfirmProcess(SignalProcess):
    """ This process waits until the job is cancelled or completed"""

    def __init__(self, trader, quote):
        super(ConfirmProcess, self).__init__(self.__class__.__name__)
        self.trader = trader
        self.quote = quote

    def confirm(self):
        yield passivate, self

        if self.have_signal("cancel"):
            self.trader.cancel_received(self.get_signal_value("cancel"))
        else:
            self.trader.complete_received(self.quote)
        


