from common_processes import *
from messages import *
from registry import *

class BrokerProcess(SignalProcess):
    def __init__(self, broker):
        super(BrokerProcess, self).__init__(self.__class__.__name__)
        self.broker = broker

    def do_broker(self):
        while 1:
            yield passivate, self

            if self.have_signal("allocate"):
                self.broker.allocate(self.get_signal_value("allocate"))
            elif self.have_signal("update"):
                self.broker.update(self.get_signal_value("update"))
            else:
                self.broker.trace("WARNING: broker woken up unexpetedly")


class ResourceUpdateProcess(SignalProcess):
    def __init__(self, agent):
        super(ResourceUpdateProcess, self).__init__(self.__class__.__name__)
        self.agent = agent

    def update(self):
        # 1st time, to avoid syncing with others, wait random time
        time = random.random() * self.agent.update_time
        yield hold, self, time

        while 1:
            self.agent.trace and self.agent.trace("sending resource state")
            state = ResourceState(self.agent, self.agent.resource.free)
            msg = Update(state)
            msg.send_msg(self.agent.node, self.agent.broker.node)
            yield hold, self, self.agent.update_time


class AllocateProcess(SignalProcess):
    def __init__(self, agent):
        super(AllocateProcess, self).__init__(self.__class__.__name__)
        self.agent = agent

    def allocate(self):

        self.agent.trace and self.agent.trace("sending allocation")
        msg = AllocationRequest(self.agent.allocation)
        msg.send_msg(self.agent.node, self.agent.broker.node)

        yield hold, self, self.agent.allocate_timeout

        if self.have_signal("response"):
            self.agent.response(self.get_signal_value("response"))
        else:
            self.agent.trace and self.agent.trace("allocation timed out")
            self.agent.fail()



