from record import *


nfailures = 0
nsucceded = 0
failure_sizes_tally = Monitor()
succeeded_sizes_tally = Monitor()
attempts_tally = Monitor()

def record_success(jagent, allocation):
    global njobs, nsucceded
    njobs += 1
    nsucceded += 1
    attempts_tally.observe(jagent.attempts)
    succeeded_sizes_tally.observe(allocation.jagent.job.size)

def record_failure(jagent, allocation):
    global njobs, nfailures
    njobs += 1
    nfailures += 1
    attempts_tally.observe(jagent.attempts)
    failure_sizes_tally.observe(allocation.jagent.job.size)

def calc_results(model):
    global results, counts
    results = general_results(model, results)

    # failure issues
    results["broker_server_util"] = stats.mean_broker_server_util(model)
    results["broker_queue_time"] = stats.mean_broker_queue_time(model)
    
    results["prop_failed"] = nfailures / float(njobs)
    results["mean_attempts"] = attempts_tally.mean()

    results["failed_sizes_mean"] = failure_sizes_tally.mean()
    results["failed_sizes_skew"] = scipy.skew([n[1] for n in failure_sizes_tally])

    results["succeeded_sizes_mean"] = succeeded_sizes_tally.mean()
    results["succeeded_sizes_skew"] = scipy.skew([n[1] for n in succeeded_sizes_tally])
    
    counts["GRID"] += 8

    counts["NET"] += 0


    return results
 



