import logging
from SimPy.Simulation import reactivate

sortedtuple = lambda *x: tuple(sorted(x))

def reactivate_on_call(func):
    def entangle(cls, *a, **kw):
        func(cls, *a, **kw)
        reactivate(cls)
    return entangle


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

    def append(self, x):
        """ append an element at the end of the buffer. """
        super(RingBuffer, self).append(x)
        if len(self) == self.max:
            self.cur = 0
            # Permanently change self's class from non-full to full
            self.__class__ = RingBuffer.__Full

