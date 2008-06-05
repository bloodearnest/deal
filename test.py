#import psyco
#psyco.full()

import sealedbid
from models import GridModel
from stats import dists
from networks import Topologies
import itertools
import trace
trace.enabled = False

test_kws = dict(
        size=1000,
        arrival_mean=0.1,
        arrival_dist=dists.constant,
        service_means=dists.normal(0.01),
        latency_means=dists.normal(0.01),
        #latency_means=dists.constant(0.1),
        #latency_dist=dists.constant,
        #topology=Topologies.test_network,
        market=sealedbid.setup
        )

model = sealedbid.SBModel(**test_kws)


model.run(until=1000)

    

                  

                  
