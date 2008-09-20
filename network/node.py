import copy
import math
import random
from itertools import izip, chain
import networkx
from trace import Tracer
from networkx import generators, connected_components, Graph, XGraph
#from stats import dists, random_other

class Node(object):
    """Basic network node."""
    def __init__(self, id, location, region, graph):
        self.id = id
        self.location = location
        self.region = region
        self.graph = graph
        self.resource_agent = None
        self.job_agents = set()
        self.old_job_agents = set()

    @property
    def neighbors(self):
        return self.graph.neighbors(self)
    
    @property
    def degree(self):
        return len(self.neighbors)

    def generate_latency(self, other):
        if self is other:
            return 0
        elif self.graph.has_edge(self, other):
            latency = self.graph.get_edge(self, other)
            return latency()
        elif self.region == other.region and hasattr(self.graph, "global_latency"):
            return self.graph.regional_latency()
        elif hasattr(self.graph, "global_latency"):
            return self.graph.global_latency()
        else:
            raise StandardError("no link and no global latency!")
            
    def confirm_job_agent(self, agent, trace):
        if agent in self.job_agents:
            return agent
        elif agent in self.old_job_agents:
            trace and trace("%s was at %s, but has moved on" % (agent, self))
        else:
            trace("WARNING: %s is not/never was at %s" % (agent, self))
        return None
        

    def __str__(self):
        return "node %d" % self.id

    def __lt__(self, other):
        return self.id < other.id

    __repr__ = __str__

    def shout_msg(self, msg, *a, **kw):
        ttl = kw.get('ttl', 0)
        trace = Tracer(self).add('m%-11d' % msg.msgid)

        if ttl > 0:
            # send copy of the same message on to all neighbours
            ttl -= 1
            sent_some = False
            old_history = msg.history
            msg.history = old_history.union(self.neighbors)

            for dst in self.neighbors: # always send to self
                if dst not in old_history: # not already seen
                    sent_some = True
                    if trace:
                        trace("shouting on to %s (ttl %d)" % (dst, ttl))
                    # SimPy requires 1:1 Process:PEM, so we copy
                    msg_copy = msg.clone()
                    msg_copy.send_msg(self, dst, ttl=ttl)
                else:
                    trace and trace("ttl %d, %s in msg history, not passing on" % (ttl, dst))
            if not sent_some:
                trace and trace("message received everywhere before ttl expired")
        else:
            trace and trace("ttl expired")



