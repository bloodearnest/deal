from copy import deepcopy
from trace import Tracer
from processes import *
from record import mdsrecord as record
from registry import *


class SyncDict(dict):
    def __init__(self, broker, *a, **kw):
        super(SyncDict, self).__init__(*a, **kw)
        self.broker = broker

class Broker(object):

    def __init__(self, region, node, registry, sync_time, others):
        self.region = region
        self.node = node
        self.registry = registry
        self.sync_time = sync_time
        self.others = others
        self.listen_process = None
        self.trace = Tracer(node).add("bkr%-9s" % region)

    def __str__(self):
        return "broker %d" % self.region

    def start(self):
        self.listen_process = BrokerListenProcess(self)
        self.listen_process.start(self.listen_process.listen())
        self.update_process = BrokerUpdateProcess(self)
        self.update_process.start(self.update_process.update())

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

    @property
    def other_brokers(self):
        for other in self.others.itervalues():
            if other is not self:
                yield other

    def send_sync(self):
        states = SyncDict(self)
        for agent, state in self.registry.states.iteritems():
            states[agent] = ResourceState(agent, state.free)

        for other in self.other_brokers:
            self.trace and self.trace("sending sync to %s" % other)
            msg = SyncMessage(states)
            msg.send_msg(self.node, other.node)


    def sync(self, states):
        self.trace and self.trace("syncing states from %s" % states.broker)
        for state in states.itervalues():
            self.registry.update_state(state)

