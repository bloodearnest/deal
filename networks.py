import random
import networkx
from networkx import generators, connected_components, Graph, XGraph

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

    def __str__(self):
        return "node %d" % self.id

def generate_network(generator, node_type=Node):
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
    for n in graph:
        G.add_node(node_type(n, G))
    for a, b in G.edges_iter():
        G.add_edge(a, b, None)

    return G

class Topologies(object):

    @staticmethod
    def random(n, p):
        return lambda: generators.random_graphs.fast_gnp_random_graph(n,p)

    @staticmethod
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


class Latencies(object):

    @staticmethod
    def random(means):
        def gen(graph):
            for n1, n1, latency in graph.edges_iter():
                graph.add_edge(n1, n2, means())
        return gen

