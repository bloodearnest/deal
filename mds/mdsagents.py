from trace import Tracer
from processes import *
from messages import *
from registry import *
from record import mdsrecord as record
from agents import *

class MdsJobAgent(JobAgent):
    def __init__(self, job, allocate_timeout, accept_timeout, max_attempts):
        JobAgent.__init__(self, job)
        self.allocate_timeout = allocate_timeout
        self.accept_timeout = accept_timeout
        self.allocation = Allocation(self, None)
        self.attempts = 0
        self.max_attempts = max_attempts
        

    @property
    def broker(self):
        return self.node.broker

    def send_allocation_request(self):
        if self.attempts < self.max_attempts:
            self.allocation = Allocation(self, None)
            self.attempts += 1
            self.trace and self.trace("sending allocation (%s)", self.attempt)
            self.allocate_process = AllocateProcess(self)
            self.allocate_process.start(self.allocate_process.allocate())
            msg = AllocationRequest(self.allocation)
            msg.send_msg(self.node, self.broker.node)
        else:
            self.trace and self.trace("allocation attemps execeeded")
            self.record_failure(self.allocation)
            self.cancel_all()

    def start(self):
        self.send_allocation_request()

    def start_on(self, node):
        self.node = node
        self.node.job_agents.add(self)
        self.trace = Tracer(self.node).add("jagent%-6s" % self.job.id)
        self.trace = self.trace.add("j%-5s" % self.job.id)
        self.start()

    def response(self, alloc):
        self.trace and self.trace("got allocation: %s" % alloc)
        if (alloc.ragent):
            self.allocation = alloc
            self.trace and self.trace("sending accept to %s" % alloc.ragent)
            self.start_accept_process(alloc.ragent, alloc, self.accept_timeout)
        else:
            self.trace and self.trace("broker gave null alloc")
            self.send_allocation_request()
            

    def allocate_timedout(self):
        self.trace and self.trace("allocation request timedout")
        self.send_allocation_request()


    #internal AcceptProcess interface
    def confirm_received(self, confirm):
        if confirm == self.allocation:
            self.trace and self.trace("accept confirmed")
            self.record_success(confirm)
            self.cancel_all()
            self.accept_process = None

        elif confirm in self.timedout: # old confirms
            self.trace and self.trace("got confirm from timed out quote")
        else: # unknown confirm
            self.trace("WARNING: got random confirm: %s" % confirm)

    def reject_received(self, reject):
        if reject == self.allocation: # allocation rejected
            self.trace and self.trace("accept rejected")
            self.send_allocation_request()

        elif reject in self.timedout:
            self.trace and self.trace("accept rejected, but had already timed out")
        else:
            self.trace("WARNING: got reject for unknown quote: %s" % reject)
   
    def accept_timedout(self, accept):
        self.trace and self.trace(" accept timed out, sending cancel")
        cancel = Cancel(self, accept.ragent, accept)
        cancel.send_msg(self.node, accept.ragent.node)
        self.send_allocation_request()


    def record_failure(self, alloc):
        record.record_failure(self, alloc)

    def record_success(self, alloc):
        record.record_success(self, alloc)


    def __str__(self):
        return "jagent%d" % self.job.id


class MdsResourceAgent(ResourceAgent):
    def __init__(self, node, update_time):
        ResourceAgent.__init__(self, node)
        self.update_time = update_time
        self.update_process = None
        self.listen_process = None
        self.trace = Tracer(self.node).add("ragent%-6s" % node.id)

    def accept(self, value):
        if self.listen_process:
            self.listen_process.signal("accept", value)
        else:
            self.trace("WARNING: no listen process for accept")

    @property
    def broker(self):
        return self.node.broker

    def start(self):
        self.update_process = ResourceUpdateProcess(self)
        self.update_process.start(self.update_process.update())
        self.listen_process = ResourceListenProcess(self)
        self.listen_process.start(self.listen_process.listen())

    # accept received
    def accept_received(self, alloc):
        job = alloc.jagent.job
        trace = self.trace.add("j%-5s" % job.id)
        if self.resource.can_allocate(job):
            trace and trace("accept from %s, starting" % alloc.jagent)
            self.confirm_and_start_job(job, alloc.jagent, alloc)
        else:
            trace and trace("accept from %s, busy, rejecting" % alloc.jagent)
            self.send_reject(alloc.jagent, alloc)


    def __str__(self):
        return "ragent%d" % self.node.id


