from processes import *
from messages import *

class Agent(object):
    def __init__(self):
        self.brokers = []

    def add_broker(self, broker):
        self.brokers.append(broker)

class ResourceAgent(Agent):
    def __init__(self, node):
        super(ResourceAgent, self).__init__(self)
        self.node = node
        self.resource = resource
        self.update_process = None
        self.confirm_processes = dict()

    def start(self):
        self.update_process = ResourceUpdateProcess(self)
        self.update_process.start(self.update_process.update())


class JobAgent(Agent):
    def __init__(self, job):
        super(ResourceAgent, self).__init__(self)
        self.job = job
        self.allocate_process = None
        self.accept_process = None
        self.allocation = (job, None)

    def start(self):
        self.allocate_process = AllocateProcess(self)
        self.allocate_process.start(self.allocate_process.allocate())

    def start_on(self, node):
        self.node = node
        self.start()





    

