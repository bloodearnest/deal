#import model
#from base import BaseModel
from models import GridModel
from networks import Topologies

size=100
arrive=0.1

m = GridModel(size=size, arrival=arrive)
m.run(until=500)


import stats
print stats.mean_server_utilisation(m)
print stats.mean_queue_time(m)

