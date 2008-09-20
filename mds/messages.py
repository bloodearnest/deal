from message import Message
from record import mdsrecord as record

class Allocation(object):
    def __init__(self, jagent, ragent=None):
        self.jagent = jagent
        self.ragent = ragent

    @property
    def job(self):
        return self.jagent.job

    def __str__(self):
        return "Alloc(%s, %s)" % (self.jagent, self.ragent)


class MessageWithAllocation(Message):
    def __init__(self, allocation, *a, **kw):
        super(MessageWithAllocation, self).__init__(*a, **kw)
        self.allocation = allocation

class AllocationRequest(MessageWithAllocation):
    def process(self, src, dst, trace, **kw):
        if dst.broker:
            dst.broker.process.signal("allocate", self.allocation)
        else:
            trace("WARNING: no broker for allocate request at node %s" %
                    (dst.id))

class AllocationResponse(MessageWithAllocation):
    def process(self, src, dst, trace, **kw):
        id = self.allocation.jagent.job.id
        if id in dst.job_agents:
            dst.job_agents[id].allocate_process.signal("response", self.allocation)
        else:
            trace("WARNING: agent %s not found at %s" % (id, dst))

class Update(Message):
    def __init__(self, state, **kw):
        super(Update, self).__init__()
        self.state = state

    def process(self, src, dst, trace, **kw):
        if dst.broker:
            dst.broker.process.signal("update", self.state)
        else:
            trace("WARNING: no broker for allocate request at node %s" %
                    (dst.id))







