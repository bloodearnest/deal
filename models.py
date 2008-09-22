import random
from model import Model
from grid import Server, GridResource, Job
from stats import dists
import stats
import network
from odict import OrderedDict
from SimPy.Simulation import Monitor

class GridModel(Model):
    "Basic model of the Grid"
    def __init__(self,
                 size=100,
                 load=1.0,
                 regions=(4,4),
                 coords=(100,100),
                 run_times=3,
                 arrival_dist = dists.expon,
                 resource_sizes = dists.gamma(100),
                 job_sizes = dists.gamma(20),
                 job_durations = dists.gamma(100),
                 service_means = dists.normal(0.1),
                 service_dist = dists.gamma,
                 latency_means = dists.normal(0.1),
                 latency_dist = dists.gamma,
                 regional_latency = dists.gamma(0.2),
                 global_latency = dists.gamma(0.4)
                 ):


        # calculated results
        self.runtime = run_times * job_durations.mean
        total_capacity = size * resource_sizes.mean;
        max_jobs = total_capacity / float(job_sizes.mean);
        arrival_mean = job_durations.mean / float(max_jobs);

        self.inter_arrival_time = arrival_dist(arrival_mean / load)
        self.job_sizes = job_sizes
        self.job_durations = job_durations
        
        # store for stats
        self.size = size
        self.load = load

        # generate network
        self.graph = network.Network(
                coords,
                regions,
                latency_means,
                regional_latency,
                global_latency,
                latency_dist)
        
        # generate nodes, but no topology
        network.generate_nodes(self.graph, size)
 
        self.service_dist = service_dist
        self.service_means = service_means
        for node in self.graph.nodes_iter():
            node.server = Server(node, service_dist(service_means()))
            node.resource = GridResource(node, int(resource_sizes()))

        self.mons = OrderedDict()
        self.mons["grid_util"] = Monitor("grid_util")
        self.mons["server_util"] = Monitor("server_util")
        self.mons["server_queue"] = Monitor("server_queue")

    @property
    def nodes(self):
        return self.graph.nodes()

    def random_node(self):
        return random.choice(self.nodes)

    def random_region_node(self, region):
        return random.choice([n for n in self.graph.nodes_iter()
                              if n.region == region])

    def new_job(self):
        return Job(self.job_sizes(), self.job_durations())

    def collect_stats(self):
        self.mons["grid_util"].observe(stats.mean_resource_util(self))
        self.mons["server_util"].observe(stats.mean_server_utilisation(self))
        self.mons["server_queue"].observe(stats.mean_queue_time(self))

    def get_series_mons(self):
        for mon in self.mons.itervalues():
            yield mon

        


