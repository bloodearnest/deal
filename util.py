import math
from SimPy.Simulation import reactivate, Tally, Monitor, Process

sortedtuple = lambda *x: tuple(sorted(x))


class RingBuffer(list):
    """ class that implements a not-yet-full buffer """
    def __init__(self, size):
        self.max = size

    class __Full(list):
        """ class that implements a full buffer """

        def append(self, x):
            """ Append an element overwriting the oldest one. """
            self[self.cur] = x
            self.cur = (self.cur+1) % self.max

        def tolist(self):
            """ return list of elements in correct order. """
            return self[self.cur:] + self[:self.cur]
        
        add = append

    def append(self, x):
        """ append an element at the end of the buffer. """
        super(RingBuffer, self).append(x)
        if len(self) == self.max:
            self.cur = 0
            # Permanently change self's class from non-full to full
            self.__class__ = RingBuffer.__Full

    add = append


class JobTracker(object):
    def __init__(self, name):
        self.name = name
        self.sizes = Monitor(name + " job sizes")
        self.limits = Monitor(name + " buyer limits")
        self.degrees = Monitor(name + " buyer node degrees")

    def record(self, quote):
        self.sizes.observe(quote.job.size)
        self.limits.observe(quote.buyer.limit)
        self.degrees.observe(len(quote.buyer.node.neighbors))

    @property
    def count(self):
        return self.sizes.count()

    def report(self):
        print self._report(self.sizes)
        print self._report(self.limits)
        print self._report(self.degrees)

    def _report(self, tally):
        s = "mean %s: %.2f (%.2f)"
        if tally.count():
            vars = (tally.name, tally.mean(), math.sqrt(tally.var()))
        else:
            vars = (tally.name, 0, 0)
        return s % vars

class SignalProcess(Process):
    def __init__(self, name=None):
        super(SignalProcess, self).__init__(name)
        self._signals = dict()
    
    def signal(self, name, value=None):
        self._signals[name] = value
        reactivate(self)

    def have_signal(self, name):
        return name in self._signals

    def get_signal_value(self, name):
        return self._signals.pop(name, None)

def reactivate_on_call(func):
    def entangle(cls, *a, **kw):
        func(cls, *a, **kw)
        reactivate(cls)
    return entangle


