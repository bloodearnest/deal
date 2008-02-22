from random import choice
if __debug__:
    from SimPy.SimulationTrace import Resource
else:
    from SimPy.Simulation import Resource

import util

class Node(object):

    def __init__(self, id, service, dist):
        self.id = id
        self.service_time = dist(service)
        self.processor = Resource(name="Processor %d" % id)
        self.links = set()
        self.msg_history = util.RingBuffer(100)

    def random_link(self):
        return choice(self.links)

    def __lt__(self, other):
        return self.id < other.id


