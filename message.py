import itertools
from copy import deepcopy

if __debug__:
    from SimPy.SimulationTrace import *
else:
    from SimPy.Simulation import *

_msg_counter = itertools.count()

class Message(Process):

    def log(self, msg):
        pass
        #print "%s at node %d: %s" % (self.name, self.dst.id, msg)

    def __init__(self, model, **kw):
        # clone msg id if passed
        self.msgid = kw.pop('msgid', None)
        self.history = kw.get('history', set())
        if not self.msgid:
            self.msgid = _msg_counter.next()
        self.model = model
        super(Message, self).__init__(name="Message %d" % self.msgid)

    def send(self, src, dst, **kw):
        self.init(src, dst, **kw)

        if self.msgid in self.dst.msg_history:
            self.log("already seen message, dropping")
            raise StopIteration
        else:
            self.dst.msg_history.append(deepcopy(self.msgid))

        if self.src != None:
            #self.log("being sent from node %d" % self.src.id)
            latency = self.model.link_latency(src, dst)
            yield hold, self, latency
            #self.log("arrived after %s" % latency)
        else:
            pass
            #self.log("arrived from source")

        # wait for the processor
        yield request, self, dst.processor
        #self.log("got processor, waited %s" % (now() - self.arrived))

        # TODO queue stats

        # simulate the work
        yield hold, self, dst.service_time()

        # do our work, sending any messages
        for msg, generator in self.process():
            activate(msg, generator)

        # release the processor
        #self.log("finished")
        yield release, self, dst.processor

    def init(self, src, dst, **kw):
        self.history.add(dst)
        self.dst = dst
        self.src = src
        self.arrived = now()

    def process(self):
        raise StopIteration
