import math, random

class FullyConnectedNode(StandardError):
    pass

def generative_link(G, node, p_local):
    # discount self and neighbors
    all_nodes = G.nodes()
    all_nodes.remove(node)
    for n in node.neighbors:
        all_nodes.remove(n)


    if random.random() < p_local: # local
        nds = [n for n in all_nodes if n.region == node.region]
    else: # global
        nds = [n for n in all_nodes if n.region != node.region]

    if not nds:
        nds = all_nodes
    
    if not all_nodes:
        print len(node.neighbors)
        print len([n for n in all_nodes if n.region == node.region])
        print len([n for n in all_nodes if n.region != node.region])
        raise FullyConnectedNode()

    return random.choice(nds)


def generative_topology(G, p_local = 0.7):
    nodes = G.nodes()
    size = len(nodes)
    max_edges = size * G.mean_degree / 2
    
    # give everyone a link
    for node in nodes:
            G.make_link(node, generative_link(G, node, p_local))
        
    edges = size
    while edges < max_edges:
        node = random.choice(nodes)
        G.make_link(node, generative_link(G, node, p_local))
        edges += 1





