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
        load=1.0,
        #service_means=dists.gamma(0.1),
        #latency_means=dists.gamma(0.1),
        #global_latency=dists.gamma(0.1),
        #topology=Topologies.alltoall(size)
        )

model = SBModel(**test_kws)
model.run()

print "actual demand q:", sum(model.bq_total), len(model.bq_total)
print "actual supply q:", sum(model.sq_total), len(model.sq_total)
import stats
import record

print "Grid:"

acc = 0

print "resource util %.2f%%" % (stats.mean_resource_util(model) * 100)
print "server util: %.2f%%" % (stats.mean_server_utilisation(model) * 100)
print "queue time: %.2fs" % stats.mean_queue_time(model)

failed = record.failures.count / float(record.njobs) * 100
print "failed: %.2f%%" % failed
record.failures.report()
record.successes.report()

print sum(record.failed.values()), record.failures.count

for reason, count in record.failed.iteritems():
    print "Failed by %s: %.2f%%" % (reason, 
                                    count/float(record.failures.count)*100)
print 

print "Economy:"
record.report()

                  

                  
