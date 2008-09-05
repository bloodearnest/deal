import math, random

class FullyConnectedNode(StandardError):
    pass

def generative_link(G, node, p_local, p_pref):
    # discount self and neighbors
    all_nodes = G.nodes()
    all_nodes.remove(node)
    for n in node.neighbors:
        all_nodes.remove(n)


    if p_local and random.random() < p_local: # local
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
    
    if p_pref and random.random() < p_pref:
        other = roulette_select(nds)
        if other:
            return other
        else:
            return random.choice(nds)
    else:
        return random.choice(nds)

def roulette_select(nds):
    choices = []
    for n in nds:
        choices += [n for i in range(n.degree)]
    if choices:
        return random.choice(choices)
    else:
        return None

def generative_topology(G, p_local = 0.0, p_pref = 0.0):
    nodes = G.nodes()
    size = len(nodes)
    max_edges = size * G.mean_degree / 2 # 1 ling = +2 degrees!
    
    # give everyone a link
    for node in nodes:
        G.make_link(node, generative_link(G, node, p_local, p_pref))
        
    edges = size
    while edges < max_edges:
        node = random.choice(nodes)
        G.make_link(node, generative_link(G, node, p_local, p_pref))
        edges += 1





