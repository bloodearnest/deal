from trace import Tracer
from processes import *
from messages import *
from registry import *
from record import mdsrecord as record

class Agent(object):

    @property
    def broker(self):
        return self.node.broker

class ResourceAgent(Agent):
    def __init__(self, node, update_time):
        self.node = node
        self.update_time = update_time
        self.resource = node.resource
        self.update_process = None
        self.confirm_processes = dict()
        self.trace = Tracer(self.node).add("ragent%-6s" % node.id)

    def start(self):
        self.update_process = ResourceUpdateProcess(self)
        self.update_process.start(self.update_process.update())

    def __str__(self):
        return "ragent%d" % self.node.id

class JobAgent(Agent):
    def __init__(self, job, allocate_time):
        self.job = job
        self.allocate_timeout = allocate_time
        self.allocate_process = None
        self.accept_process = None
        self.allocation = Allocation(self, None)
        self.trace = None

    def start(self):
        self.allocate_process = AllocateProcess(self)
        self.allocate_process.start(self.allocate_process.allocate())

    def start_on(self, node):
        self.node = node
        self.node.job_agents[self.job.id] = self
        self.trace = Tracer(self.node).add("jagent%-6s" % self.job.id)
        self.trace = self.trace.add("j%-5s" % self.job.id)
        self.start()

    def response(self, allocation):
        self.trace and self.trace("got allocation: %s" % allocation)
        record.record_success(allocation)


    def fail(self):
        record.record_failure(self.allocation)

    def __str__(self):
        return "jagent%d" % self.job.id
