import random
from SimPy.Simulation import initialize, simulate, hold, Process

class DummyProcess(Process):
    """A process that does nothing for one second"""
    def pem(self):
        yield hold, self, 1

class Model(object):

    class Generator(Process):
        def generate(self, model):
            while 1:
                model.new_process()
                yield hold, self, model.inter_arrival_time()
    
    def setup():
        pass

    def start(self):
        g = self.Generator('generator')
        g.start(g.generate(self))

    def new_process(self):
        """Generates new process entering the system"""
        p = DummyProcess("dummy process")
        p.start(p.pem())

    def run(self, *a, **kw):
        initialize()
        self.start()
        simulate(*a, **kw)
