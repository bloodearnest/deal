import random
from datetime import datetime, timedelta
from SimPy.Simulation import initialize, simulate, hold, Process, now
from guppy import hpy

class DummyProcess(Process):
    """A process that does nothing for one second"""
    def pem(self):
        yield hold, self, 1

class Model(object):

    class Generator(Process):
        def generate(self, model):
            while 1:
                yield hold, self, model.inter_arrival_time()
                model.new_process()

    class StatCollector(Process):
        def collect(self, model, n=300.0):
            interval = model.runtime / n
            tlast = 0
            while 1:
                yield hold, self, interval
                model.collect_stats(tlast)
                tlast = now()


    class Progress(Process):
        def report(self, until):
            h = hpy()
            start = datetime.now()
            last = 0
            t = until / 20
            x = 5
            while 1:
                yield hold, self, t
                now = datetime.now()
                elapsed = now - start
                guess = elapsed.seconds / float(x) * 100
                eta = start + timedelta(seconds=guess)
                print "[%s] %02d%% [ETA: %s]" % (now.strftime('%H:%M:%S'),
                                               x,
                                               eta.strftime('%H:%M:%S'))
                x += 5

    def setup():
        pass

    def start(self, *a, **kw):
        g = self.Generator('generator')
        g.start(g.generate(self))
        p = self.Progress('progress')
        p.start(p.report(self.runtime))
        c = self.StatCollector('stats')
        c.start(c.collect(self))

    def new_process(self):
        """Generates new process entering the system"""
        p = DummyProcess("dummy process")
        p.start(p.pem())

    def run(self, *a, **kw):
        kw['until'] = kw.get('until', getattr(self, 'runtime', 100))
        self.runtime = kw['until']
        initialize()      
        self.start(*a, **kw)
        simulate(*a, **kw)
