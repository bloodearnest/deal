from random import choice
from SimPy.Simulation import Resource, Tally

from util import RingBuffer

class Server(object):

    def __init__(self, node, service):
        self.service = service

        # servers processor resource, with stats
        self.processor = Resource(name="Server at %s" % node.name,
                                  monitored=True,
                                  monitorType=Tally)

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
