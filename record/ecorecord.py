from record import *
import equilibrium
from SimPy.Simulation import now, Tally, Monitor
from util import JobTracker
import networkx
buys = [] 
buys_theory = []
sells = []
sells_theory = []
trade_times = []
trade_prices = []

buyer_timeouts = Tally("buyer_timeouts")
buyer_util = Tally("buyer_util")
seller_util = Tally("seller_util")

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

#init failure reasons
for r in failure_reasons:
    failed[r] = 0
        
job_penetration_tally = Tally("job penetration")
migrations = Tally("migrations")

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

def record_failure(quote):
    failures.record(quote)
    reasons = failure_reasons_record[quote.job.id]

    rcount = dict()
    total_reasons = float(len(reasons))
    for reason in failure_reasons:
        total = len([r for r in reasons if r == reason])
        rcount[reason] = total / total_reasons

    for reason in rcount:
        failed[reason] += rcount[reason]

def record_failure_reason(jobid, reason):
    assert reason in failure_reasons
    failure_reasons_record[jobid].append(reason)

def clean_up_job(job):
    # clear up the memory using in tracking this job
    global njobs
    njobs += 1
    if job.id in failure_reasons:
        del failure_reasons[job.id]
    job_penetration_tally.observe(len(job.nodes_visited))



def calc_results(model):
    global results, counts
    results = general_results(model, results)

    # failure issues
    results["job_penetration"] = job_penetration_tally.mean() / float(model.size) * 100.0
    results["prop_failed"] = failures.count / float(njobs)
    results["mean_migrations"] = migrations.mean() / float(njobs)

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

    counts["GRID"] += 15

    for reason, count in failed.iteritems():
        r = "prop_failed_by_%s" % reason
        if failures.count:
            results[r] = count/float(failures.count)
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
    
    results["eq_price"] = real[0]
    results["eq_price_theory"] = theory[0]
    results["efficiency"] = eff
    results["mean_buyer_util"] = buyer_util.mean()
    results["mean_seller_util"] = seller_util.mean()
    counts["ECO"] += 5

    G = model.graph
    results["topology"] = getattr(model, "topology", "none")
    results["density"] = networkx.density(G)
    results["mean_degree"] = sum(len(n.neighbors) for n in G.nodes_iter()) / float(G.order())
    results["degree_skew"] = scipy.skew(networkx.degree(G))
    results["diameter"] = float(networkx.diameter(G))
    results["radius"] = float(networkx.radius(G))
    results["transitivity"] = float(networkx.transitivity(G))
    counts["NET"] += 7


    return results
 



