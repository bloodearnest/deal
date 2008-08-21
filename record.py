import math
from collections import defaultdict
from odict import OrderedDict
import networkx
from scipy import stats as scipy
import numpy
import stats
import equilibrium

from SimPy.Simulation import now, Tally, Monitor

from util import JobTracker

buys = [] 
buys_theory = []
sells = []
sells_theory = []
trade_times = []
trade_prices = []

buyer_timeouts = Tally("buyer_timeouts")
buyer_util = Tally("buyer_util")
seller_util = Tally("seller_util")

njobs = 0

successes = JobTracker("successful")
failures = JobTracker("failed")
failed = defaultdict(int)

failure_reasons_record = defaultdict(list)
failure_reasons = [
        "Too Busy",
        "Too Busy Later",
        "Timedout",
        "High Buyer Limit",
        "Unknown"
        ]

for r in failure_reasons:
    failed[r] = 0
        
job_penetration_tally = Tally("job penetration")

def record_trade(quote, success=True):
    t = now()
    successes.record(quote)

    # record trade details
    trade = (quote.price, quote.quantity, t)
    trade_times.append(t)
    trade_prices.append(quote.price)
    buys.append(trade)
    sells.append(trade)

    #record utility
    buyer_util.observe(quote.buyer.limit - quote.price)
    seller_util.observe(quote.price - quote.seller.limit)

    _clean_up_job(quote.job)

def record_failure(quote):
    failures.record(quote)
    reasons = failure_reasons_record[quote.job.id]

    rcount = defaultdict(float)
    for r in failure_reasons:
        if r in reasons:
            rcount[r] += (1 / float(len(reasons)))
        else:
            rcount[r] = 0

    for r in rcount:
        failed[r] += rcount[r]
        
    _clean_up_job(quote.job)

def record_failure_reason(jobid, reason):
    assert reason in failure_reasons
    failure_reasons_record[jobid].append(reason)


def _clean_up_job(job):
    # clear up the memory using in tracking this job
    global njobs
    njobs += 1
    if job.id in failure_reasons:
        del failure_reasons[job.id]
    job_penetration_tally.observe(len(job.nodes_visited))



counts = defaultdict(int)

def calc_results(model):
    results = OrderedDict()

    results["size"] = model.size
    results["load"] = model.load
    results["topology"] = model.topology
    counts["GENERAL"] += 3

    # grid performance
    results["resource util"] = stats.mean_resource_util(model) * 100
    results["server util"] = stats.mean_server_utilisation(model) *100 
    results["queue time"] = stats.mean_queue_time(model)
    results["job penetration"] = job_penetration_tally.mean() / float(model.size) * 100.0
    counts["GRID"] += 4

    # failure issues
    results["prop failed"] = failures.count / float(njobs) * 100

    
    results["failed_sizes_mean"] = failures.sizes.mean()
    results["failed_sizes_skew"] = scipy.skew([n[1] for n in failures.sizes])

    results["failed_limits_mean"] = failures.limits.mean()
    results["failed_limits_skew"] = scipy.skew([n[1] for n in failures.limits])

    results["failed_degrees_mean"] = failures.degrees.mean()
    results["failed_degrees_skew"] = scipy.skew([n[1] for n in failures.degrees])

    results["succeeded_sizes_mean"] = successes.sizes.mean()
    results["succeeded_sizes_skew"] = scipy.skew([n[1] for n in successes.sizes])
    
    results["succeeded_limits_mean"] = successes.limits.mean()
    results["succeeded_limits_skew"] = scipy.skew([n[1] for n in successes.limits])
    
    results["succeeded_degrees_mean"] = successes.degrees.mean()
    results["succeeded_degrees_skew"] = scipy.skew([n[1] for n in successes.degrees])

    counts["GRID"] += 13

    for reason, count in failed.iteritems():
        r = "prop failed by %s" % reason
        if failures.count:
            results[r] = count/float(failures.count) * 100
        else:
            results[r] = 0
        counts["GRID"] += 1

    # economic stuff
    buys.sort()
    buys.reverse()
    sells.sort()
    buys_theory.sort()
    buys_theory.reverse()
    sells_theory.sort()
    
    real = equilibrium.find_equilibrium(buys, sells)
    theory = equilibrium.find_equilibrium(buys_theory, sells_theory)
    eff = real[1] / theory[1] * 100
    
    results["eq price"] = real[0]
    results["eq price theory"] = theory[0]
    results["efficiency"] = eff
    results["mean buyer util"] = buyer_util.mean()
    results["mean seller util"] = seller_util.mean()
    counts["ECO"] += 5

    G = model.graph
    results["density"] = networkx.density(G)
    results["mean_degree"] = sum(len(n.neighbors) for n in G.nodes_iter()) / float(G.order())
    results["degree_skew"] = scipy.skew(networkx.degree(G))
    results["diameter"] = float(networkx.diameter(G))
    results["radius"] = float(networkx.radius(G))
    results["transitivity"] = float(networkx.transitivity(G))
    counts["NET"] += 6


    return results
 



