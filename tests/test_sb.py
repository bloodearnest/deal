from .. import sealedbid
from ..models import GridModel
from ..stats import dists
from ..networks import Topologies
from .. import market


model = GridModel(10, 
                  arrival_mean = 1,
                  arrival_dist = dists.constant,
                  service_means = dists.constant(1),
                  service_dist = dists.constant,
                  latency_means = dists.constant(1),
                  latency_dist = dists.constant,
                  topology = Topologies.test_network,
                  market=sealedbid.setup)

def test_model():
    assert len(model.graph.nodes()) == 10
    nodes = model.graph.nodes()
    nodes.sort(key =lambda n:n.id)
    n0 = nodes[0]
    n1 = nodes[1]
    n2 = nodes[2]
    assert model.graph.neighbors(n0) == [n1]
    assert sorted(model.graph.neighbors(n1)) == [n0, n2]

    

                  

                  
