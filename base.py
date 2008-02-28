import random

from model import Model
from message import Message

from networks import Node, Network, Topologies
from grid import Server
from stats import dists

class BaseModel(Model):
    def __init__(self,
                 size,
                 arrival=1,
                 mean_degree=2,
                 mean_services = dists.normal(1, 0.25),
                 service_dist = dists.gamma,
                 mean_latencies = dists.normal(1, 0.25),
                 latency_dist = dists.gamma,
                 topology = Topologies.random):

        super(BaseModel, self).__init__(arrival)

        self.size = size
        self.mean_latencies = mean_latencies
        self.latency_dist = latency_dist

        # generate network nodes
        self.nodes = Network(Node(i) for i in range(size))
        # generate the connections on the network
        topology(self.nodes, mean_degree, mean_latencies, latency_dist)

        # add model specific components
        for node in self.nodes:
            node.server = Server(node, service_dist(mean_services()))


    def new_process(self):
        dst = self.nodes.random_node()
        msg = Message(self)
        return msg, msg.send(None, dst)


