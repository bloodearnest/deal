#import psyco
#psyco.full()

from models import GridModel
from stats import dists
from networks import Topologies
import itertools
import trace
trace.enabled = False

from sealedbid.model import SBModel, setup

test_kws = dict(
        size=1000,
        arrival_mean=0.1,
        arrival_dist=dists.expon,
        service_means=dists.gamma(0.2),
        latency_means=dists.gamma(0.2),
        latency_dist=dists.gamma,
        #topology=Topologies.test_network,
        market=setup
        )

model = SBModel(**test_kws)


model.run(until=500)

import stats
import record

#print stats.mean_server_utilisation(model)
#print stats.mean_queue_time(model)

record.report()

                  

                  
