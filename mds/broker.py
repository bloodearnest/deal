from trace import Tracer
from processes import *
from record import mdsrecord as record

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
        trace = self.trace.add("j%-5s" % allocation.jagent.job.id)
        
        trace and trace("alloc request from %s" % allocation.jagent)
        states = self.registry.get_resources(allocation)
        # return the best system wide fit
        states.sort(key=lambda x: x.free)

        if states:
            state = states[0]
            alloc = Allocation(allocation.jagent, state.agent)
            msg = AllocationResponse(alloc)
            msg.send_msg(self.node, alloc.jagent.node)
            trace and trace("returning alloc %s" % alloc)
        else:
            trace and trace("no valid allocations")


    def update(self, state):
        self.trace and self.trace("updating state for %s" % state.agent)
        self.registry.update_state(state)



