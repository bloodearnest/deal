import random
from model import Model
from networks import Node, generate_network, Topologies, Latencies
from grid import Server, GridResource, Job
from stats import dists

from messages import BroadcastMessage

class GridModel(Model):

    def __init__(self,
                 size,
                 arrival=1,
                 mean_degree=2,
                 resource_size_means = dists.gamma(100),
                 job_size_means = dists.gamma(20),
                 job_duration_means = dists.gamma(100),
                 service_means = dists.normal(1, 0.25),
                 service_dist = dists.gamma,
                 latency_means = dists.normal(1, 0.25),
                 latency_dist = dists.gamma,
                 topology = None,
                 latencies = None):

        super(GridModel, self).__init__(arrival)

        # defaults
        topology = topology or Topologies.random_by_degree(size, mean_degree);
        latencies = latencies or Latencies.random(latency_means)

        # generate network
        self.graph = generate_network(topology)
        # add latency weights to graph
        latencies(self.graph)

        # add model specific components
        for node in self.graph.nodes_iter():
            node.server = Server(node, service_dist(service_means()))
            node.resource = GridResource(node, int(resource_size_means()))
            node.seller = None

    @property
    def nodes(self):
        return self.graph.nodes()

    def random_node(self):
        return random.choice(self.nodes)

    def new_process(self):
        dst = self.random_node()
        msg = BroadcastMessage(self)
        return msg, msg.send(None, dst, ttl=2)

