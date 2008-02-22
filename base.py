import random

from model import Model
from message import Message

from grid import Node
from stats import dists
import networks

class BaseModel(Model):
    def __init__(self,
                 size,
                 arrival=1,
                 mean_degree=2,
                 mean_services = dists.normal(1, 0.25),
                 service_dist = dists.gamma,
                 mean_latencies = dists.normal(1, 0.25),
                 latency_dist = dists.gamma,
                 network = networks.random):

        super(BaseModel, self).__init__(arrival)
        self.size = size

        # generate network nodes
        # TODO: generalise this with node factory function
        self.nodes = [Node(i, mean_services(), service_dist)
                      for i in range(size)]

        # network 
        # TODO generalise with with factory function
        self.degree = mean_degree
        self.links = {}
        self.mean_latencies = mean_latencies
        self.latency_dist = latency_dist
        network(self) # build network

    def new_process(self):
        dst = self.random_node()
        msg = Message(self)
        return msg, msg.send(None, dst)


    # network related methods
    def _rand_node(self):
        return random.randint(0, self.size - 1)

    def random_node_id(self, exclude=-1):
        node = self._rand_node()
        while node == exclude:
            node = self._rand_node()
        return node

    def random_node(self, exclude=None):
        exclue = exclude and exclude.id or -1
        return self.nodes[self.random_node_id(exclude)]

    def link_latency(self, node, other):
        """Generate a latency between two links, using their variate generator
        latency."""
        link = tuple(sorted((node, other))) # sorted tuple is dict key
        return self.links[link]()
