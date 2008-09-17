from processes import *

class Broker(object):

    def __init__(self, region, node, registry):
        self.region = region
        self.node = node
        self.registry = registry
        self.process = None

    def start(self):
        self.process = BrokerProcess()
        self.process.start(self.process.broker())

    def allocate(self, job):
        resources = self.registry.get_resources(job)
        # return the best system wide fit
        resources.sort(key=lambda x: x.free)

    def update(self, state):
        self.registry.update_state(state)



