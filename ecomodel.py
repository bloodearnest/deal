from models import GridModel
from grid import Server, GridResource, Job
from stats import dists
import network
from record import ecorecord as record
from SimPy.Simulation import Monitor, now

class EcoModel(GridModel):

    def __init__(self, 
            mean_degree=8,
            ttl=1,
            p_local = 0.0,
            p_pref = 0.0,
            p_social = 0.0,
            **kw):
        super(EcoModel, self).__init__(**kw)
        self.buyer_ttl = ttl

        network.generative_topology(self.graph,
                mean_degree, p_local, p_pref, p_social)

        self.topology = "generative"

        self.mons["price"] = Monitor("price")

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

    def collect_stats(self, tlast):
        super(EcoModel, self).collect_stats(tlast)
        self.mons["price"].observe(record.collect_avg_price())


    def print_node(self, n, tlast):
        print "%.2f: node %02d: %03d/%0.2f/%d: %.2f/%.2f/%.2f" % (
               now(),
               n.id,
               n.resource.capacity,
               n.resource_agent.limit,
               len(n.neighbors),
               n.resource.current_util(tlast), 
               n.server.current_util(tlast),
               n.server.current_queue(tlast)
               )




        


