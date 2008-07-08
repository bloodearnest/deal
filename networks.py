import copy
import random
from itertools import izip, chain
import networkx
from networkx import generators, connected_components, Graph, XGraph
from trace import Tracer
from stats import dists, random_other

MAX_NETGEN_ATTEMPTS = 5

class Node(object):
    """Basic network node."""
    def __init__(self, id, graph):
        self.id = id
        self.graph = graph

    @property
    def neighbors(self):
        return self.graph.neighbors(self)

    def generate_latency(self, other):
        if self.graph.has_edge(self, other):
            latency = self.graph.get_edge(self, other)
            return latency()
        elif hasattr(self.graph, "global_latency"):
            return self.graph.global_latency()
        else:
            raise StandardError("no link and no global latency!")
            
    def confirm_buyer(self, buyer):
        if buyer not in self.buyers:
            raise StandardError("%s not found at %s" % (buyer, self))

    def __str__(self):
        return "node %d" % self.id

    def __lt__(self, other):
        return self.id < other.id

    __repr__ = __str__

    def shout_msg(self, msg, *a, **kw):
        ttl = kw.get('ttl', 3)
        trace = Tracer(self).add('m%-7d' % msg.msgid)

        if ttl:
            # send copy of the same message on to all neighbours
            ttl -= 1
            sent_some = False
            old_history = msg.history
            msg.history = old_history.union(self.neighbors)

            for dst in self.neighbors:
                if dst not in old_history: # not already seen
                    sent_some = True
                    if trace:
                        trace("passing on to %s (ttl %d)" % (dst, ttl))
                    # SimPy requires 1:1 Process:PEM, so we copy
                    #msg_copy = copy.copy(msg)
                    msg_copy = msg.clone()
                    msg_copy.send_msg(self, dst, ttl=ttl)
                else:
                    trace and trace("ttl %d, %s in history, not passing on" % (ttl, dst))
            if not sent_some:
                trace and trace("message received everywhere before ttl expired")
        else:
            trace and trace("ttl expired")



def generate_network(generator, node_type=Node, draw=True):
    count = 0
    graph = generator()
    while len(networkx.connected_components(graph)) != 1:
        if count >= MAX_NETGEN_ATTEMPTS:
            raise StandardError("network with single giant component "
                                "could not be generated")
        graph = generator()
        count += 1

    # bleh messy I want Node objects as nodes, not ints
    G = networkx.XGraph()
    G.add_nodes_from(node_type(n, G) for n in graph)
    nodes = sorted(G.nodes(), key=lambda n:n.id)
    for a, b in graph.edges_iter():
        G.add_edge(nodes[a], nodes[b], 0)

    return G

def name_return(f):
    def entangle(*a, **kw):
        x = f(*a, **kw)
        x.__name__ = f.__name__
        return x
    return entangle

class Topologies(object):

    @staticmethod
    @name_return
    def random(n, p):
        x = lambda: generators.random_graphs.fast_gnp_random_graph(n,p)

    @staticmethod
    @name_return
    def random_by_degree(n, degree):
        def gen():
            g = networkx.Graph()
            nodes = range(n)
            g.add_nodes_from(nodes)

            for node in g.nodes_iter():
                other = random_other(nodes, node)
                g.add_edge(node, other)

            # fill up the rest
            for i in range(len(nodes), len(nodes) * degree):
                node = random.choice(nodes)
                other = random_other(nodes, node)
                g.add_edge(node, other)
            return g
        return gen

    @staticmethod
    @name_return
    def test_network():
        g = networkx.Graph()
        nodes = range(10)
        g.add_nodes_from(nodes)
        for a, b in izip(nodes, nodes[1:]):
            g.add_edge(a, b)
        return g

    @staticmethod
    @name_return
    def alltoall(n):
        def gen():
            g = networkx.Graph()
            g.add_nodes_from(range(n))
            nodes = g.nodes()
            for n1 in nodes:
                for n2 in nodes:
                    if n2 > n1:
                        g.add_edge(n1, n2)
            return g
        return gen

    


        



class Latencies(object):

    @staticmethod
    def random(means, dist):
        def gen(graph):
            for n1, n2, latency in graph.edges_iter():
                graph.add_edge(n1, n2, dist(means()))
        return gen

