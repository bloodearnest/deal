from SimPy.Simulation import *

from models import GridModel
from market import MarketRules
from traders import ZIC, ZIP
from stats import dists

from buyer import SBBuyer
from seller import SBSeller

slimits = dists.uniform_int(20, 400)
#slimits = dists.constant(2.5)
blimits = dists.uniform(200, 500)
#blimits = dists.constant(2.5)
rules = MarketRules()
rules.min = 1
rules.max = 1000
trader = ZIC

def setup(graph):
    for n in graph.nodes_iter():
        r = trader(False, slimits(), rules)
        n.seller = SBSeller(n.id, n, 60, r, rules)

class SBModel(GridModel):
    def new_process(self):
        #x = sum(n.seller.rationale.quote() for n in self.nodes)
        #print x / float(self.graph.size())
        dst = self.random_node()
        job = self.new_job()
        r = trader(True, blimits(), rules)
        buyer = SBBuyer(job.id, dst, 10, r)
        dst.buyers.add(buyer)
        return buyer, buyer.trade(job)




