#import model
#from base import BaseModel
from models import BroadcastModel

size=10000
arrive=0.001


#m = model.Model()
#m = BaseModel(size=100, arrival=0.1)
m = BroadcastModel(size=size, arrival=arrive)
m.run(until=300)


import stats
print stats.mean_server_utilisation(m)
print stats.mean_queue_time(m)

