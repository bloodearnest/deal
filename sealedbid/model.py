import random
import networks
from models import GridModel
from market import MarketRules
from traders import ZIC, ZIP
from stats import dists

from buyer import SBBuyer
from seller import SBSeller

slimits = dists.uniform_int(50, 100)
blimits = dists.uniform_int(400, 500)
rules = MarketRules()
rules.min = 1
rules.max = 500
trader = ZIP


class SBModel(GridModel):

    def new_buyer(self, job, dst):
        r = trader(True, blimits(), rules)
        buyer = SBBuyer(job.id, dst, 5, r, self.buyer_ttl)
        dst.buyers.add(buyer)
        buyer.start(buyer.trade(job))
        return buyer

    def setup(self):
        for n in self.graph.nodes_iter():
            r = trader(False, slimits(), rules)
            r.price = random.randint(r.limit, rules.max)
            n.seller = SBSeller(n.id, n, 60, r, rules)




