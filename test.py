#import psyco
#psyco.full()

import sealedbid
from models import GridModel
from stats import dists
from networks import Topologies
import itertools
import trace
#trace.enabled = False

test_kws = dict(
        size=100,
        arrival_mean=0.1,
        arrival_dist=dists.expon,
        service_means=dists.gamma(0.2),
        latency_means=dists.gamma(0.2),
        latency_dist=dists.gamma,
        #topology=Topologies.test_network,
        market=sealedbid.setup
        )

model = sealedbid.SBModel(**test_kws)


model.run(until=200)

import stats
print stats.mean_server_utilisation(model)
print stats.mean_queue_time(model)

                  

                  
