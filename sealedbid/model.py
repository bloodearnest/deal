import random
from ecomodel import EcoModel
from market import MarketRules
from rationales import ZIC, ZIP
from stats import dists

from buyer import SBBuyer
from seller import SBSeller

slimits = dists.uniform_int(50, 200)
blimits = dists.uniform_int(300, 500)
rules = MarketRules()
rules.min = 1
rules.max = 500
rationale = ZIP


class SBModel(EcoModel):

    def new_buyer(self, job, node):
        buyer = SBBuyer(
                job, 
                rationale(True, blimits(), rules),
                ttl=self.buyer_ttl, 
                quote_timeout = 5,
                accept_timeout = 10)
        buyer.start_on_node(node)
        return buyer

    def __init__(self, **kw):
        super(SBModel, self).__init__(**kw)

        # set the sellers up
        for n in self.graph.nodes_iter():
            r = rationale(False, slimits(), rules)
            r.price = random.randint(r.limit, rules.max)
            n.resource_agent = SBSeller(
                    n, 
                    r,
                    quote_timeout=30,
                    accept_timeout=20
                    )




