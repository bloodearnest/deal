from random import choice
from SimPy.Simulation import Resource, Tally

from util import RingBuffer

class Node(object):

    def __init__(self, id, service, dist):
        self.id = id
        self.name = "Node %d" % id
        self.service_time = dist(service) # service time generator

        # servers processor resource, with stats
        self.processor = Resource(name="Processor %d" % id,
                                  monitored=True,
                                  monitorType=Tally)

        # node's network data
        self.links = set()                      # links to other nodes

        # recent history of messages, to avoid re-handling
        self.msg_history = RingBuffer(100)


    @property
    def mean_queue_wait(self):
        """The time waited mean wait for the processor."""
        return self.processor.waitMon.timeAverage()

    @property
    def mean_utilisation(self):
        """The time waited mean processor utilisation."""
        return self.processor.actMon.timeAverage()

    def __lt__(self, other):
        """id comparision, allows sorted pairs of nodes as a dict key."""
        return self.id < other.id

    # network functions
    def random_link(self):
        """Choose a random link from this nodes links."""
        return choice(self.links)
