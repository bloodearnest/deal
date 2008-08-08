import itertools
from random import choice
from SimPy.Simulation import Process, Resource, Tally, hold

from util import RingBuffer

class Server(object):

    def __init__(self, node, service):
        self.id = node.id
        self.service_time = service

        # servers processor resource, with stats
        self.processor = Resource(name="Server at %s" % node,
                                  monitored=True,
                                  monitorType=Tally)

        # recent history of messages, to avoid re-handling
        self.msg_history = RingBuffer(300)

    def __str__(self):
        return "server %d" % self.id

    @property
    def mean_queue_wait(self):
        """The time waited mean wait for the processor."""
        return self.processor.waitMon.timeAverage()

    @property
    def mean_utilisation(self):
        """The time waited mean processor utilisation."""
        return self.processor.actMon.timeAverage()


class GridResource(object):
    def __init__(self, node, capacity):
        self.node = node
        self.capacity = capacity
        self.jobs = set()
        self.util = Tally("Resource %d utilisation" % node.id)

    def can_allocate(self, job):
        return job.size <= self.free

    def start(self, job):
        assert self.can_allocate(job)
        self.jobs.add(job)
        self.util.observe(self.load)
        # the job will complete and remove itself at the right time
        job.start(job.execute(self))

    def cancel(self, job):
        self.remove(job)
        # cancel previously scheduled finish event, w/SimPy work arround
        canceller = Process()
        canceller.cancel(job)

    def remove(self, job):
        assert job in self.jobs
        self.jobs.remove(job)
        self.util.observe(self.load)

    @property
    def used(self):
        return sum(job.size for job in self.jobs)

    @property
    def free(self):
        return self.capacity - self.used

    @property
    def load(self):
        return self.used / float(self.capacity)

    @property
    def utilisation(self):
        return self.util.timeAverage()



class Job(Process):
    _job_counter = itertools.count()

    def __init__(self, size, duration):
        self.id = Job._job_counter.next()
        super(Job, self).__init__("Job %d" % self.id)
        self.size = size
        self.duration = duration
        self.nodes_visited = set()

    def execute(self, resource):
        yield hold, self, self.duration     # TODO: add runtime variation
        resource.remove(self)

    @property
    def quantity(self):
        return self.size * self.duration


