import random
from stats import dists
from util import sortedtuple

class Node(object):
    """Basic netowrk node."""
    def __init__(self, id):
        self.id = id
        self.name = "Node %d" % id
        self.links = set()  # links to other nodes

    def __lt__(self, other):
        """id comparision, allows sorted pairs of nodes as a dict key."""
        return self.id < other.id

    def __eq__(self, other):
        """id comparision"""
        return self.id == other.id

    def random_node(self):
        """Choose a random node from this nodes links."""
        return random.choice(self.links)


class Network(list):
    """A networked list of nodes."""
    def __init__(self, *a, **kw):
        super(Network, self).__init__(*a, **kw)
        self.links = {}

    def random_node(self, exclude=None):
        node = random.choice(self)
        while exclude and node == exclude:
            node = random.choice(self)
        return node

    def random_link_from(self, node, latency):
        other = self.random_node(exclude=node)
        while not self.link(node, other, latency):
            other = self.random_node(exclude=node)

    def link(self, node, other, latency):
            pair = sortedtuple(node, other)
            if pair in self.links or node == other:
                return False # cannot link
            else:
                self.links[pair] = latency
                node.links.add(other)
                other.links.add(node)
                return True

    def link_latency(self, node, other):
        """Generate a latency value for the link between two nodes."""
        return self.links[sortedtuple(node, other)]()


class Topologies(object):

    @staticmethod
    def random(nodes, mean_degree, means, dist):
        for node in nodes:
            nodes.random_link_from(node, dist(means())) # give everyone one link
        for i in range(len(nodes), len(nodes) * mean_degree):
            nodes.random_link_from(nodes.random_node(), dist(means()))

    @staticmethod
    def alltoall(nodes, mean_degree, means, dist):
        for node in nodes:
            for other in nodes:
                if node != other:
                    nodes.link(node, other, dist(means()))
