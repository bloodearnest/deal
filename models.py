import random
from model import Model
from grid import Server, GridResource, Job
from stats import dists
import record
import network

#from messages import BroadcastMessage

class GridModel(Model):

    def __init__(self,
                 size=100,
                 load=1.0,
                 run_times=3,
                 arrival_dist = dists.expon,
                 mean_degree=4,
                 resource_sizes = dists.gamma(100),
                 job_sizes = dists.gamma(20),
                 job_durations = dists.gamma(100),
                 service_means = dists.normal(0.1),
                 service_dist = dists.gamma,
                 latency_means = dists.normal(0.1),
                 latency_dist = dists.gamma,
                 global_latency = dists.gamma(0.1),
                 latencies = None,
                 ttl = 1):


        # calculated results
        self.runtime = run_times * job_durations.mean
        total_capacity = size * resource_sizes.mean;
        max_jobs = total_capacity / float(job_sizes.mean);
        arrival_mean = job_durations.mean / float(max_jobs);

        self.inter_arrival_time = arrival_dist(arrival_mean / load)
        self.job_sizes = job_sizes
        self.job_durations = job_durations

        # generate network
        self.graph = network.Network(
                mean_degree,
                (100,100),
                (3,3),
                latency_means,
                global_latency,
                latency_dist)
        
        network.generate_nodes(self.graph, size)
        network.generative_topology(self.graph)
        self.topology = "generative"
        
        # store for stats
        self.size = size
        self.load = load
        self.buyer_ttl = ttl

        # add model specific components
        for node in self.graph.nodes_iter():
            node.server = Server(node, service_dist(service_means()))
            node.resource = GridResource(node, int(resource_sizes()))
            node.seller = None
            node.buyers = set()
            node.buyer_ids = set()

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
            record.sells_theory.append((n.seller.limit,
                                        n.resource.capacity * time,
                                        0))
            n.seller.start_on(n)
        super(GridModel, self).start(*a, **kw)

        


