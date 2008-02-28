import random
from SimPy.Simulation import *

class DummyProcess(Process):
    """A process that does nothing for one second"""
    def pem(self):
        yield hold, self, 1

class Model(object):
    def __init__(self, arrival=1):
        self.inter_arrival_time = lambda: random.expovariate(1.0/arrival)

    class Generator(Process):
        def generate(self, model):
            while 1:
                activate(*model.new_process())
                yield hold, self, model.inter_arrival_time()

    def start(self):
        g = self.Generator('generator')
        activate(g, g.generate(self))

    def new_process(self):
        """Generates new process entering the system"""
        p = DummyProcess("dummy process")
        return p, p.pem()

    def run(self, *a, **kw):
        initialize()
        self.start()
        simulate(*a, **kw)
