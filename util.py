import logging

sortedtuple = lambda *x: tuple(sorted(x))

class LogProxy(object):
    log_methods = frozenset(('debug', 'info', 'warning', 'critical', 'error'))

    def __init__(self, obj):
        self.logger = logging.getLogger('trace')
        self.kw = dict(object=str(obj))

    def __getattr__(self, attr):
        if attr in self.log_methods:
            def proxy_func(*a, **kw):
                kw['extra'] = self.kw
                return getattr(self.logger, attr)(*a, **kw)
            return proxy_func
        else:
            return getattr(self.logger, attr)


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

