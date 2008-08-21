import math, random
from networkx import XGraph
from node import Node

class Network(XGraph):

    def __init__(self,
            mean_degree,
            coord_space, 
            regions, 
            local_latencies,
            global_latency,
            latency_dist, 
            distance_weight = 0.3, *a, **kw):

        super(Network, self).__init__(*a, **kw)

        self.mean_degree = mean_degree
        self.coord_space = coord_space 
        self.regions = regions
        self.local_latencies = local_latencies
        self.latency_dist = latency_dist
        self.global_latency = global_latency
        self.distance_weight = distance_weight

        self.max_distance = math.sqrt((self.coord_space[0]/2)**2 + 
                                      (self.coord_space[1]/2)**2 ) 


    def latency_function(self, node1, node2):
        distance = wrapped_distance(node1.location, node2.location, self.coord_space)
        real_mean = self.local_latencies()
        w = distance / self.max_distance
        mean =  real_mean * (1 - self.distance_weight + self.distance_weight * w)
        return self.latency_dist(mean)

    def make_link(self, node, other):
        latency = self.latency_function(node, other)
        self.add_edge(node, other, latency)



def generate_nodes(G, n):
    for i in range(n):
        location, region = generate_location(G.regions, G.coord_space)
        node = Node(i, location, region, G)
        G.add_node(node)

def generate_location(regions, cspace):
    regions_x, regions_y = regions
    x_lim, y_lim = cspace
    x, y = random.random() * x_lim, random.random() * y_lim
    rx = int(x * regions_x / x_lim)
    ry = int(y * regions_y / y_lim)
    region = regions_x * ry + rx
    return (x,y), region

def wrapped_distance(a, b, maxv):
    x1 = min(a[0], b[0])
    x2 = max(a[0], b[0])
    y1 = min(a[1], b[1])
    y2 = max(a[1], b[1])
    max_x, max_y = maxv
    x = min(x2 - x1, x1 + (max_x - x2))
    y = min(y2 - y1, y1 + (max_y - y2))
    return math.sqrt(x*x + y*y)

