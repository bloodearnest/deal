import random
if __debug__:
    from SimPy.SimulationTrace import *
else:
    from SimPy.Simulation import *

class Model(object):
    """Sets up a simple SimPy simulation.

    Handles the "generator" Process, and assumes an exponential inter arrival
    time. Helps get rid of the boiler plate in setting up a simulation.

    To use, subclass and override any setup in __init__, and new_process method to
    add new Process's into the system. If you have more complex needs, you can
    override the start method to setup the simulation prior to running
    """

    def __init__(self, arrival=1):
        self.inter_arrival_time = lambda: random.expovariate(1.0/arrival)

    class Generator(Process):
        """SimPy Process object that injects Processes into the system."""
        def generate(self, model):
            while 1:
                activate(*model.new_process())
                yield hold, self, model.inter_arrival_time()

    def start(self):
        """Default start up.

        Only override if you can't generate all your events with one Process."""

        g = self.Generator('generator')
        activate(g, g.generate(self))

    class DummyProcess(Process):
        """A process that does nothing for one second"""
        def pem(self):
            yield hold, self, 1

    def new_process(self):
        """Generates new process entering the system"""
        p = Model.DummyProcess("dummy process")
        return p, p.pem()

    def run(self, *a, **kw):
        initialize()
        self.start()
        simulate(*a, **kw)
