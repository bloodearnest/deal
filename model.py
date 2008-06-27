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

    class Progress(Process):
        def report(self, time):
            t = time / 20
            x = 5
            while 1:
                yield hold, self, t
                print "%d%%" % x
                x += 5

    def setup():
        pass

    def start(self, *a, **kw):
        g = self.Generator('generator')
        g.start(g.generate(self))
        p = self.Progress('progress')
        p.start(p.report(kw['until']))

    def new_process(self):
        """Generates new process entering the system"""
        p = DummyProcess("dummy process")
        p.start(p.pem())


    def run(self, *a, **kw):
        initialize()      
        self.start(*a, **kw)
        simulate(*a, **kw)
