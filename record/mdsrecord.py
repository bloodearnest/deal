from record import *


nfailures = 0
nsucceded = 0
failure_sizes_tally = Monitor()
succeeded_sizes_tally = Monitor()

def record_success(allocation):
    global njobs, nsucceded
    njobs += 1
    nsucceded += 1
    succeeded_sizes_tally.observe(allocation.jagent.job.size)

def record_failure(allocation):
    global njobs, nfailures
    njobs += 1
    nfailures += 1
    failure_sizes_tally.observe(allocation.jagent.job.size)

def calc_results(model):
    global results, counts
    results = general_results(model, results)

    # failure issues
    results["prop_failed"] = nfailures / float(njobs) * 100
    #results["mean_migrations"] = migrations.mean() / float(njobs) * 100

    results["failed_sizes_mean"] = failure_sizes_tally.mean()
    results["failed_sizes_skew"] = scipy.skew([n[1] for n in failure_sizes_tally])

    results["succeeded_sizes_mean"] = succeeded_sizes_tally.mean()
    results["succeeded_sizes_skew"] = scipy.skew([n[1] for n in succeeded_sizes_tally])
    
    counts["GRID"] += 5

    counts["NET"] += 0


    return results
 



