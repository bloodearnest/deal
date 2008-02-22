from models import BroadcastModel
model = BroadcastModel(size=100, arrival=0.1)
model.run(until=100)

import stats
print "util:", stats.mean_server_utilisation(model)
print "wait:", stats.mean_queue_time(model)

