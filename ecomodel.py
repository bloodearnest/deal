from models import GridModel
from grid import Server, GridResource, Job
from stats import dists
import network
from record import ecorecord as record


class EcoModel(GridModel):

    def __init__(self, mean_degree=8, ttl=1, **kw):
        super(EcoModel, self).__init__(**kw)

        self.graph.mean_degree = mean_degree
        self.buyer_ttl = ttl

        network.generative_topology(self.graph)
        self.topology = "generative"

    # to be overridden
    def new_buyer(self, job, node):
        return None

    def new_process(self):
        dst = self.random_node()
        job = self.new_job()
        buyer = self.new_buyer(job, dst)
        record.buys_theory.append((buyer.limit, job.quantity, 0))

    def start(self, *a, **kw):
        time = kw["until"]
        for n in self.graph.nodes_iter():
            record.sells_theory.append(
                (n.resource_agent.limit, n.resource.capacity * time, 0)
            )
            n.resource_agent.start()
        super(EcoModel, self).start(*a, **kw)

    def calc_results(self):
        return record.calc_results(self)

        


