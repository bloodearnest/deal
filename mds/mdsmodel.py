import random
from models import GridModel
import network
import record
from broker import Broker
from agents import *
from registry import *
from messages import *

class MdsModel(GridModel):

    def __init__(self, 
            registry_type=Registry,
            **kw):
        super(MdsModel, self).__init__(**kw)

        regions = self.graph.regions
        self.regions = [(i,j) for i in range(regions[0]) 
                              for j in range(regions[1])]

        self.brokers = dict()
        for r in regions:
            node = self.random_region_node(r)
            broker = Broker(r, node, registry_type())
            self.brokers[r] = broker

        for node in self.graph.nodes_iter():
            node.broker = self.brokers[node.region]
            # this nodes resource agent
            node.resource_agent = ResourceAgent(node) 
            # mapping of jobagents at this node
            node.job_agents = dict()

            #make a link to fast comms to the broker
            self.graph.make_link(node, node.broker.node)

    def new_process(self):
        node = self.random_node()
        job = self.new_job()
        agent = JobAgent(job)
        agent.add_broker(node.broker)
        agent.start_on(node)

    def start(self, *a, **kw):
        for n in self.graph.nodes_iter():
            n.resource_agent.start()
        for b in self.brokers.values_iter():
            b.start()
        super(EcoModel, self).start(*a, **kw)

        


