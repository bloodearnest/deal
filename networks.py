from stats import dists

upair = lambda a,b: tuple(sorted((a,b)))

def random_link(model, node, latency):
    other = model.random_node(exclude=node)
    while not link_nodes(model, node, other, latency):
        other = model.random_node(exclude=node)

def link_nodes(model, node, other, mean):

        # hashable/comparable link "id"
        pair = upair(node, other)

        if pair in model.links or node.id == other.id:
            return False # cannot link
        else:
            #print "linking %d and %d with mean latency %s" % (node.id, other.id,
            #        mean)
            dist = model.latency_dist(mean)
            model.links[pair] = dist
            node.links.add(other)
            other.links.add(node)
            return True

def random(model):
    n = 0
    for node in model.nodes:
        random_link(model, node, model.mean_latencies())
        n += 1

    for i in range(n, model.size * model.degree):
        node = model.random_node()
        random_link(model, node, model.mean_latencies())
