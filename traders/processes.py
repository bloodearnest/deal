from common_processes import *

#general trading process
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


class RationaleTimeout(Process):
    def timeout(self, agent, id, quote, timeout, trace):
        yield hold, self, timeout
        agent.process_quote_timeout(id, quote, trace)



