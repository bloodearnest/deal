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
                 load=0.5,
                 run_times=3,
                 arrival_dist = dists.expon,
                 mean_degree=2,
                 resource_sizes = dists.gamma(100),
                 job_sizes = dists.gamma(20),
                 job_durations = dists.gamma(100),
                 service_means = dists.normal(0.1),
                 service_dist = dists.gamma,
                 latency_means = dists.normal(0.1),
                 latency_dist = dists.gamma,
                 global_latency = dists.gamma(0.1),
                 topology = None,
                 latencies = None):


        self.runtime = run_times * job_durations.mean
        
        # calculated results
        duration = job_durations.mean;
        total_capacity = size * resource_sizes.mean;
        max_jobs = total_capacity / float(job_sizes.mean);
        print "max_jobs", max_jobs
        arrival_mean = duration / float(max_jobs);
        print "old mean:", arrival_mean

        d = (self.runtime / arrival_mean * job_sizes.mean * job_durations.mean)
        s = (size * resource_sizes.mean * self.runtime)

        print "expected demand q:", d 
        print "expected supply q:", s

        #total_supply = size * resource_sizes.mean * run_times
        #njobs = total_supply / float(job_sizes.mean * job_durations.mean)
        #arrival_mean = njobs / float(run_times * job_durations.mean)
        #print "new mean:", arrival_mean

        self.inter_arrival_time = arrival_dist(arrival_mean * load)
        self.job_sizes = job_sizes
        self.job_durations = job_durations

        # defaults
        topology = topology or Topologies.random_by_degree(size, mean_degree);
        latencies = latencies or Latencies.random(latency_means, latency_dist)

        # generate network
        self.graph = generate_network(topology, draw=True)
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

        self.bq_total = []
        self.sq_total = []


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
        self.bq_total.append(job.quantity)
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
            self.sq_total.append(n.resource.capacity * time)

        super(GridModel, self).start(*a, **kw)


