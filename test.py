#import psyco
#psyco.full()

from models import GridModel
from stats import dists
from networks import Topologies
import itertools
import trace
trace.enabled = False

from sealedbid.model import SBModel

size = 100
test_kws = dict(
        size=size,
        load=0.5,
        #service_means=dists.gamma(0.1),
        #latency_means=dists.gamma(0.1),
        #global_latency=dists.gamma(0.1),
        #topology=Topologies.alltoall(size)
        )

model = SBModel(**test_kws)
model.run()
#record.save_results(model, 'results')

import report

report.grid(model)
report.economy(model)


                  
