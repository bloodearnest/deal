from message import MessageWithQuote
import record

class MessageWithAllocation(Message)
    def __init__(self, allocation, *a, **kw):
        super(MessageWithAllocation, self).__init__(*a, **kw)
        self.allocation = allocation

class AllocationRequest(MessageWithAllocation):
    def process(self, src, dst, trace, **kw):
        if dst.broker:
            dst.broker.signal("allocate", self.allocation)
        else:
            trace("WARNING: no broker for allocate request at node %s" %
                    (dst.id))

class AllocationResponse(MessageWithAllocation):
    def process(self, src, dst, trace, **kw):
        id = self.allocation[0].id
        if id in dst.agents:
            dst.agents[id].signal("response", self.allocation)
        else:
            trace("WARNING: agent %s not found at %s" % (id, dst))


class Update(Message):
    def __init__(self, state, **kw):
        super(Update, self).__init__(self)
        self.state = state

    def process(self, src, dst, trace, **kw):
        if dst.broker:
            dst.broker.signal("update", self.state)
        else:
            trace("WARNING: no broker for allocate request at node %s" %
                    (dst.id))







