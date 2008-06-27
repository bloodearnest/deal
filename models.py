import random
from model import Model
from networks import Node, generate_network, Topologies, Latencies
from grid import Server, GridResource, Job
from stats import dists
import record

#from messages import BroadcastMessage

class GridModel(Model):

    def __init__(self,
                 size=100,
                 arrival_mean=1,
                 arrival_dist = random.expovariate,
                 mean_degree=2,
                 resource_sizes = dists.gamma(100),
                 job_sizes = dists.gamma(20),
                 job_durations = dists.gamma(100),
                 service_means = dists.normal(0.1),
                 service_dist = dists.gamma,
                 latency_means = dists.normal(0.1),
                 latency_dist = dists.gamma,
                 global_latency = dists.gamma(0.5),
                 topology = None,
                 latencies = None):

        self.inter_arrival_time = arrival_dist(arrival_mean)
        self.job_sizes = job_sizes
        self.job_durations = job_durations
        # defaults
        topology = topology or Topologies.random_by_degree(size, mean_degree);
        latencies = latencies or Latencies.random(latency_means, latency_dist)

        # generate network
        self.graph = generate_network(topology)
        self.graph.global_latency = global_latency
        # add latency weights to graph
        latencies(self.graph)

        # add model specific components
        for node in self.graph.nodes_iter():
            node.server = Server(node, service_dist(service_means()))
            node.resource = GridResource(node, int(resource_sizes()))
            node.seller = None
            node.buyers = set()

        # do model specific setup
        self.setup()


    @property
    def nodes(self):
        return self.graph.nodes()

    def random_node(self):
        return random.choice(self.nodes)

    def new_buyer(self, job, node):
        return None

    def new_process(self):
        dst = self.random_node()
        job = self.new_job()
        buyer = self.new_buyer(job, dst)
        record.buys_theory.append((buyer.limit, job.quantity, 0))

    def new_job(self):
        return Job(self.job_sizes(), self.job_durations())

    def start(self, *a, **kw):
        time = kw["until"]
        for n in self.graph.nodes_iter():
            n.seller.start(n.seller.trade())
            record.sells_theory.append((n.seller.limit,
                                        n.resource.capacity * time,
                                        0))

        super(GridModel, self).start(*a, **kw)


