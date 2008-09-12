from models import GridModel
import network
import record
from broker import Broker
from registry import *
from messages import *

class MdsModel(GridModel):

    def __init__(self, 
            brokers=1,
            registry_type=Registry,
            **kw):
        super(MdsModel, self).__init__(**kw)

        
        # add model specific components
        for node in self.graph.nodes_iter():
            node.resource_agent = ResourceAgent(node)
            node.broker = None
            node.agents = dict()

        brokers = []
        for i in range(brokers):
            node = self.random_node()
            node.broker = Broker(node.id, node, registry_type())
            brokers.append(broker)

        self.brokers = brokers

        # random for no
        for node in self.graph.nodes_iter():
            broker = node.broker or random.choice(brokers)
            node.resource_agent.add_broker(broker)

    # to be overridden
    def new_process(self):
        dst = self.random_node()
        job = self.new_job()
        buyer = Agent(job, dst)
        buyer.add_broker(random.choice(self.brokers))
        Agent.start()

    def start(self, *a, **kw):
        time = kw["until"]
        for n in self.graph.nodes_iter():
            n.resource_agent.start()
            if n.broker:
                n.broker.start()
        super(EcoModel, self).start(*a, **kw)

        


