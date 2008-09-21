from record import *

attempts_tally = Monitor()

def record_success(jagent, alloc):
    all_record_success(jagent, alloc.job)
    attempts_tally.observe(jagent.attempts)

def record_failure(jagent, alloc):
    all_record_failure(jagent, alloc.job)
    attempts_tally.observe(jagent.attempts)

def calc_results(model):
    global results, counts
    results = general_results(model, results)

    # failure issues
    results["broker_server_util"] = stats.mean_broker_server_util(model)
    results["broker_queue_time"] = stats.mean_broker_queue_time(model)
    results["mean_attempts"] = attempts_tally.mean()

    counts["MDS"] += 3

    return results
 



