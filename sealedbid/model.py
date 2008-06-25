from models import GridModel
from market import MarketRules
from traders import ZIC, ZIP
from stats import dists

from buyer import SBBuyer
from seller import SBSeller

slimits = dists.uniform_int(20, 400)
#slimits = dists.constant(2.5)
blimits = dists.normal_int(400, 100)
#blimits = dists.constant(2.5)
rules = MarketRules()
rules.min = 1
rules.max = 1000
trader = ZIP


class SBModel(GridModel):

    def new_buyer(self, job, dst):
        #x = sum(n.seller.rationale.quote() for n in self.nodes)
        #print int(x / float(self.graph.size()))
        r = trader(True, blimits(), rules)
        buyer = SBBuyer(job.id, dst, 10, r)
        dst.buyers.add(buyer)
        buyer.start(buyer.trade(job))

    def setup(self):
        for n in self.graph.nodes_iter():
            r = trader(False, slimits(), rules)
            n.seller = SBSeller(n.id, n, 60, r, rules)




