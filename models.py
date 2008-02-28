import random
from model import Model
from networks import Node, Network, Topologies
from grid import Server, GridResource, Job
from stats import dists

from messages import BroadcastMessage

class GridModel(Model):
    def __init__(self,
                 size,
                 arrival=1,
                 mean_degree=2,
                 mean_resources = dists.gamma(100),
                 mean_job_sizes = dists.gamma(20),
                 mean_job_durations = dists.gamma(40),
                 mean_services = dists.normal(1, 0.25),
                 service_dist = dists.gamma,
                 mean_latencies = dists.normal(1, 0.25),
                 latency_dist = dists.gamma,
                 topology = Topologies.random):

        super(GridModel, self).__init__(arrival)

        self.size = size

        # generate network nodes
        self.nodes = Network(Node(i) for i in range(size))

        # generate the topological connections on the network
        topology(self.nodes, mean_degree, mean_latencies, latency_dist)

        # add model specific components
        for node in self.nodes:
            node.server = Server(node, service_dist(mean_services()))
            node.resource = GridResource(node.id, int(mean_resources()))
            node.seller = None

    def new_process(self):
        dst = self.nodes.random_node()
        msg = BroadcastMessage(self)
        return msg, msg.send(None, dst, ttl=2)

