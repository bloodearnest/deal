#import model
#from base import BaseModel
from models import BroadcastModel

size=100
arrive=0.1


#m = model.Model()
#m = BaseModel(size=100, arrival=0.1)
m = BroadcastModel(size=100, arrival=0.1)
m.run(until=100)


#import tsim
#initialize()
#g = model.Generator()
#activate(g, g.generate())
#simulate(until=100)



