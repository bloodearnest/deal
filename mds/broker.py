from trace import Tracer
from processes import *

class Broker(object):

    def __init__(self, region, node, registry):
        self.region = region
        self.node = node
        self.registry = registry
        self.process = None
        self.trace = Tracer(node).add("bkr%-9s" % region)

    def start(self):
        self.process = BrokerProcess(self)
        gen = self.process.do_broker()
        self.process.start(gen)

    def allocate(self, allocation):

        states = self.registry.get_resources(allocation)
        # return the best system wide fit
        states.sort(key=lambda x: x.free)

        if states:
            state = states[0]
            alloc = Allocation(allocation.jagent, state.agent)
            self.trace and self.trace("returning allocation")
            msg = AllocationResponse(alloc)
            msg.send_msg(self.node, alloc.jagent.node)
        else:
            self.trace and self.trace("no valid allocations")


    def update(self, state):
        self.registry.update_state(state)



