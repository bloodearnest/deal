import math, random

def local_link(p_local):
    def get_link(G, nodes, node):
        nds = nodes
        if random.random() < p_local:
            nds = [n for n in nodes if n.region == node.region and n != node]
            if len(nds) == 0:
                nds = nodes 
        return random.choice(nds)
    return get_link

def generate_topology(G, get_link=local_link(0.6)):

    nodes = list(G.nodes())
    max_edges = len(nodes) * G.mean_degree

    for node in nodes:
        other = get_link(G, nodes, node)
        latency = G.latency_function(node, other)
        G.add_edge(node, other, latency)

    edges = len(nodes)

    while edges < max_edges:
        node = random.choice(nodes)
        other = get_link(G, nodes, node)
        latency = G.latency_function(node, other)
        G.add_edge(node, other, latency)
        edges += 1



