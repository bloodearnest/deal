import random
from ecomodel import EcoModel
from market import MarketRules
from rationales import ZIC, ZIP
from stats import dists

from buyer import SBBuyer
from seller import SBSeller

slimits = dists.uniform_int(50, 100)
blimits = dists.uniform_int(400, 500)
rules = MarketRules()
rules.min = 1
rules.max = 500
rationale = ZIP


class SBModel(EcoModel):

    def new_buyer(self, job, node):
        r = rationale(True, blimits(), rules)
        buyer = SBBuyer(job.id, r, job, ttl=self.buyer_ttl, )
        buyer.start_on_node(node)
        return buyer

    def __init__(self, **kw):
        super(SBModel, self).__init__(**kw)

        # set the sellers up
        for n in self.graph.nodes_iter():
            r = rationale(False, slimits(), rules)
            r.price = random.randint(r.limit, rules.max)
            n.seller = SBSeller(n.id, r, n,
                    quote_timout=60,
                    accept_timeout=60
                    )




