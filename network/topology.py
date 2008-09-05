import math, random
from itertools import chain

class FullyConnectedNode(StandardError):
    pass

def valid_node_choices(G, node):
    # discount self and neighbors
    nodes = G.nodes()
    nodes.remove(node)
    for n in node.neighbors:
        nodes.remove(n)
    return nodes

def generative_link(G, node, p_local, p_pref, p_social):

    nodes = []
    local = p_local and random.random() < p_local

    if p_social and node.neighbors and random.random() < p_social: 
        # get a list of my friends
        if local:
            friends = [n for n in node.neighbors if n.region == node.region]
            if not friends: # force not local
                friends = node.neighbors
        else:
            friends = node.neighbors

        # get a list of friends of friends that I'm not already friends with
        fofs = set(fof for fof in chain(*(f.neighbors for f in friends))
                   if fof != node and fof not in friends)
        nodes = list(fofs)
    else:
        nodes = valid_node_choices(G, node)
        if local:
            nodes = [n for n in nodes if n.region == node.region]
        else: # global
            # should we force non-local here? or make it random?
            nodes = [n for n in nodes if n.region != node.region]

    if not nodes:
        print "WARNING: edge " + G.size() + " generated links choice not valid"
        nodes = valid_node_choices(G, node)
    
    if not nodes:
        print "neighbors:", len(node.neighbors)
        print "local:", len([n for n in nodes if n.region == node.region])
        print "other:", len([n for n in nodes if n.region != node.region])
        raise FullyConnectedNode()
    
    if p_pref and random.random() < p_pref:
        return roulette_select(nodes)
    else:
        return random.choice(nodes)

def roulette_select(nds):
    choices = nds
    for n in nds:
        choices += [n for i in range(n.degree)]
    return random.choice(choices)

def generative_topology(G, p_local = 0.0, p_pref = 0.0, p_social=0.5):
    nodes = G.nodes()
    size = len(nodes)
    max_edges = size * G.mean_degree / 2 # 1 ling = +2 degrees!
    
    # give everyone a link
    for node in nodes:
        G.make_link(node, generative_link(G, node, p_local, p_pref, p_social))
        
    edges = size
    while edges < max_edges:
        node = random.choice(nodes)
        G.make_link(node, generative_link(G, node, p_local, p_pref, p_social))
        edges += 1





