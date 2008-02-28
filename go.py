import logging
from models import GridModel
from networks import Topologies

size=100
arrive=0.1

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)-8s:%(object)-12s: %(message)s')

m = GridModel(size=size, arrival=arrive)
m.run(until=500)


import stats
print stats.mean_server_utilisation(m)
print stats.mean_queue_time(m)

