import random
from models import GridModel
import network
import record
from broker import Broker
from agents import *
from registry import *
from messages import *
from record import mdsrecord as record

class MdsModel(GridModel):

    def __init__(self, 
            registry_type=Registry,
            **kw):
        super(MdsModel, self).__init__(**kw)

        regions = self.graph.regions
        self.regions = [i for i in range(regions[0]*regions[1])]

        self.brokers = dict()
        for r in self.regions:
            node = self.random_region_node(r)
            broker = Broker(r, node, registry_type())
            self.brokers[r] = broker

        for node in self.graph.nodes_iter():
            node.broker = self.brokers[node.region]
            # this nodes resource agent
            node.resource_agent = ResourceAgent(node, 30) 
            # mapping of jobagents at this node
            node.job_agents = dict()

            # make a link to fast comms to the broker
            self.graph.make_link(node, node.broker.node)

    def new_process(self):
        node = self.random_node()
        job = self.new_job()
        agent = JobAgent(job, 20)
        agent.start_on(node)

    def start(self, *a, **kw):
        for n in self.graph.nodes_iter():
            n.resource_agent.start()
        for b in self.brokers.itervalues():
            b.start()
        super(MdsModel, self).start(*a, **kw)

    def calc_results(self):
        return record.calc_results(self)

        


