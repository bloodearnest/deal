import itertools
from SimPy.Simulation import *

_msg_counter = itertools.count()

class Message(Process):

    def log(self, msg):
        print "%s at node %d: %s" % (self.name, self.dst.id, msg)

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
            # TODO collect dropped stats
            self.log("already seen message, dropping")
            raise StopIteration
        else:
            self.dst.msg_history.append(self.msgid)

        if self.src != None:
            self.log("being sent from node %d" % self.src.id)
            latency = self.model.link_latency(src, dst)
            yield hold, self, latency
            self.log("arrived after %s" % latency)
        else:
            pass
            self.log("arrived from source")

        # wait for the processor, recording waiting stats
        yield request, self, dst.processor

        self.log("got processor, waited %s" % (now() - self.arrived))

        # simulate the work
        yield hold, self, dst.service_time()

        self.log("calling process")
        # do our work, sending any messages
        for msg in self.process():
            activate(*msg)

        # release the processor
        yield release, self, dst.processor
        self.log("finished")

    def init(self, src, dst, **kw):
        self.history.add(dst)
        self.dst = dst
        self.src = src
        self.arrived = now()

    def process(self):
        """null iterator"""
        if False:
            yield None # never executes, but converts function to generator
        raise StopIteration

    def __del__(self):
        self.log("collected")
