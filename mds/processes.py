from messages import *
from common_processes import *

class BrokerProcess(SignalProcess):
    def __init__(self, broker):
        super(Broker, self).__init__(self.__class__.__name__)
        self.broker = broker

    def broker(self):
        while 1:
            yield passivate, self

            if self.have_signal("allocate"):
                broker.allocate(self.get_signal_value("allocate"))
            elif self.have_signal("update"):
                broker.update(self.get_signal_value("update"))
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
            state = ResourceState(agent.id, agent.resource.free)
            for broker in agent.brokers:
                msg = Update(state)
                msg.send_msg(self.agent.node, broker.node)
            yield hold, self, self.agent.update_time


class AllocateProcess(SignalProcess):
    def __init__(self, agent):
        super(AllocateProcess, self).__init__(self.__class__.__name__)
        self.agent = agent

    def allocate(self):
        msg = AllocationRequest(agent.allocation)

        msg.send_msg(agent.node, agent.broker.node)

        yield hold, self, agent.allocate_timeout

        if self.have_signal("response")
            agent.response(self.get_signal_value("response"))
        else
            agent.trace and agent.trace("allocation timed out")



