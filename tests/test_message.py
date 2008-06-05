from cStringIO import StringIO
from SimPy.Simulation import *
from .. import message
from .. import networks
from ..stats import dists

class TestMessage(message.Message):
    def process(self, src, dst, log, **kw):
        print "TestMessage arrived at %s at time %s" % (dst, now())

class TestServer(object):
    msg_history = []
    processor = Resource(1)
    service_time = lambda s: 1

G = networks.generate_network(networks.Topologies.test_network)
networks.Latencies.random(dists.constant(1), dists.constant)(G)
for n in G.nodes_iter():
    n.server = TestServer()

Nodes = G.nodes()
Nodes.sort()

def test_message():
    n0, n1 = Nodes[0], Nodes[1]
    msg = TestMessage()
    initialize()
    activate(msg, msg.send(n0, n1))
    simulate(until=10)
    assert False
    

