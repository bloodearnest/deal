from record import *
import equilibrium
from SimPy.Simulation import now, Tally, Monitor
from util import JobTracker
import networkx
from stats import skew
from scipy import stats as scipy


# eco stats 
buys = [] 
buys_theory = []
sells = []
sells_theory = []
trade_times = []
trade_prices = []

buyer_timeouts = Tally("buyer_timeouts")
buyer_util = Tally("buyer_util")
seller_util = Tally("seller_util")


trackers = [ 
    ("limits", lambda x,y: x.limit),
    ("degrees", lambda x,y: len(x.node.neighbors) )
]
eco_succeeded_tracker = JobTracker("succeeded", trackers)
eco_failed_tracker = JobTracker("failed", trackers)

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

price_window = []
def collect_avg_price():
    global price_window
    if not price_window:
        return 0
    mean = sum(price_window) / float(len(price_window))
    price_window = []
    return mean

def record_success(agent, quote):
    global price_window
    all_record_success(agent, quote.job)
    eco_succeeded_tracker.record(agent, quote.job)
    price_window.append(quote.price)
    t = now()
    # record trade details
    trade = (quote.price, quote.quantity, t)
    trade_times.append(t)
    trade_prices.append(quote.price)
    buys.append(trade)
    sells.append(trade)

    #record utility
    buyer_util.observe(quote.buyer.limit - quote.price)
    seller_util.observe(quote.price - quote.seller.limit)
    
    common_stats(agent, quote)

def record_failure(agent, quote):
    all_record_failure(agent, quote.job)
    eco_failed_tracker.record(agent, quote.job)
    reasons = failure_reasons_record[quote.job.id]

    rcount = dict()
    total_reasons = float(len(reasons))
    for reason in failure_reasons:
        total = len([r for r in reasons if r == reason])
        rcount[reason] = total / total_reasons

    for reason in rcount:
        failed[reason] += rcount[reason]

    common_stats(agent, quote)

def common_stats(agent, quote):
    job_penetration_tally.observe(len(quote.job.nodes_visited))
    migrations.observe(agent.migrations)

    # clear up the memory using in tracking this job
    if quote.job.id in failure_reasons:
        del failure_reasons[job.id]

def record_failure_reason(jobid, reason):
    assert reason in failure_reasons
    failure_reasons_record[jobid].append(reason)

def calc_results(model):
    global results, counts
    results = general_results(model, results)

    # failure issues
    results["job_penetration"] = job_penetration_tally.mean() / float(model.size) * 100.0
    results["mean_migrations"] = migrations.mean() / float(njobs.total)

    results["failed_limits_mean"] = eco_failed_tracker.limits.mean()
    results["failed_limits_skew"] = stats.skew(eco_failed_tracker.limits)

    results["failed_degrees_mean"] = eco_failed_tracker.degrees.mean()
    results["failed_degrees_skew"] = stats.skew(eco_failed_tracker.degrees)

    results["succeeded_limits_mean"] = eco_succeeded_tracker.limits.mean()
    results["succeeded_limits_skew"] = stats.skew(eco_succeeded_tracker.limits)
    
    results["succeeded_degrees_mean"] = eco_succeeded_tracker.degrees.mean()
    results["succeeded_degrees_skew"] = stats.skew(eco_succeeded_tracker.degrees)

    counts["ECO"] += 10

    for reason, count in failed.iteritems():
        r = "prop_failed_by_%s" % reason
        if eco_failed_tracker.count:
            results[r] = count/float(eco_failed_tracker.count)
        else:
            results[r] = 0
        counts["ECO"] += 1

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
    results["mean_degree"] = model.graph.mean_degree
    results["p_local"] = model.graph.p_local
    results["p_pref"] = model.graph.p_pref
    results["p_social"] = model.graph.p_social
    results["density"] = networkx.density(G)
    results["mean_degree"] = sum(len(n.neighbors) for n in G.nodes_iter()) / float(G.order())
    results["degree_skew"] = scipy.skew(networkx.degree(G))
    results["diameter"] = float(networkx.diameter(G))
    results["radius"] = float(networkx.radius(G))
    results["transitivity"] = float(networkx.transitivity(G))
    counts["NET"] += 10


    return results
 



