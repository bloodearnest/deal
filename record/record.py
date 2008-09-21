import math
from collections import defaultdict
from odict import OrderedDict
import numpy
import stats
from util import JobTracker

from SimPy.Simulation import now, Tally, Monitor

class NJobs(object):
    failed = 0
    succeeded = 0

    @property
    def total(self):
        return self.failed + self.succeeded

    @property
    def prop_failed(self):
        return self.failed / float(self.total)

njobs = NJobs()

counts = defaultdict(int)
results = OrderedDict()

trackers = [ 
    ("sizes", lambda x,y: y.size),
    ("times", lambda x,y: now() - x.start_time)
]
succeeded_tracker = JobTracker("succeeded", trackers)
failed_tracker = JobTracker("failed", trackers)

def all_record_success(agent, job):
    njobs.succeeded += 1
    succeeded_tracker.record(agent, job)

def all_record_failure(agent, job):
    njobs.failed += 1
    failed_tracker.record(agent, job)

def general_results(model, results):
    global nfailed, nsucceeded

    results["size"] = model.size
    results["load"] = model.load
    counts["GENERAL"] += 2

    # grid performance
    results["resource_util"] = stats.mean_resource_util(model)
    results["server_util"] = stats.mean_server_utilisation(model)
    results["queue_time"] = stats.mean_queue_time(model)
    results["prop_failed"] = njobs.prop_failed
    
    results["succeed_sizes_mean"] = succeeded_tracker.sizes.mean()
    results["succeed_sizes_skew"] = stats.skew(succeeded_tracker.sizes)

    results["succeed_times_mean"] = succeeded_tracker.times.mean()
    results["succeed_times_skew"] = stats.skew(succeeded_tracker.times)
    
    results["failed_sizes_mean"] = failed_tracker.sizes.mean()
    results["failed_sizes_skew"] = stats.skew(failed_tracker.sizes)
    
    results["failed_times_mean"] = failed_tracker.times.mean()
    results["failed_times_skew"] = stats.skew(failed_tracker.times)
    
    counts["GRID"] += 12

    return results

