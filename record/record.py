import math
from collections import defaultdict
from odict import OrderedDict
from scipy import stats as scipy
import numpy
import stats

from SimPy.Simulation import now, Tally, Monitor

#general statistics
njobs = 0
counts = defaultdict(int)
results = OrderedDict()
def general_results(model, results):

    results["size"] = model.size
    results["load"] = model.load
    counts["GENERAL"] += 2

    # grid performance
    results["resource_util"] = stats.mean_resource_util(model)
    results["server_util"] = stats.mean_server_utilisation(model)
    results["queue_time"] = stats.mean_queue_time(model)
    counts["GRID"] += 3

    return results

