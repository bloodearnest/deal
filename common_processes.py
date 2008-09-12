from SimPy.Simulation import *
from util import SignalProcess

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


class AcceptProcess(SignalProcess):
    def __init__(self, agent, value, timeout):
        super(AcceptProcess, self).__init__(self.__class__.__name__)
        self.agent = agent
        self.value = value
        self.timeout = timeout

    def accept(self):
        yield hold, self, self.timeout

        # we have a confirmed accept
        if self.have_signal("confirm"):
            self.agent.confirm_received(self.get_signal_value("confirm"))

        elif self.have_signal("reject"):
            self.agent.reject_received(self.get_signal_value("reject"))

        # we have timed out on accept
        else:
            self.agent.accept_timedout(self.value)


class ConfirmProcess(SignalProcess):
    """ This process waits until the job is cancelled or completed"""

    def __init__(self, agent, value):
        super(ConfirmProcess, self).__init__(self.__class__.__name__)
        self.agent = agent
        self.value = value

    def confirm(self):
        yield passivate, self

        if self.have_signal("cancel"):
            self.agent.cancel_received(self.get_signal_value("cancel"))
        else:
            self.agent.complete_received(self.value)
            
 


