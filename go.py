#import model
#from base import BaseModel
from models import BroadcastModel
from networks import Topologies

size=100
arrive=0.1


#m = model.Model()
#m = BaseModel(size=100, arrival=0.1)
m = BroadcastModel(size=size, arrival=arrive, topology=Topologies.alltoall)
m.run(until=300)


import stats
print stats.mean_server_utilisation(m)
print stats.mean_queue_time(m)

