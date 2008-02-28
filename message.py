import itertools
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

        if self.msgid in dst.server.msg_history:
            # TODO collect dropped stats
            self.log("already seen message, dropping")
            raise StopIteration
        else:
            dst.server.msg_history.append(self.msgid)

        if src != None:
            self.log("being sent from node %d" % src.id)
            latency = self.model.nodes.link_latency(src, dst)
            yield hold, self, latency
            self.log("arrived after %s" % latency)
        else:
            pass
            self.log("arrived from source")

        # wait for the processor, recording waiting stats
        yield request, self, dst.server.processor

        self.log("got processor, waited %s" % (now() - self.arrived))

        # simulate the work
        yield hold, self, dst.server.service()

        self.log("calling process")
        # do our work, sending any messages
        for msg in self.process(src, dst, **kw):
            activate(*msg)

        # release the processor
        yield release, self, dst.server.processor
        self.log("finished")

    def init(self, src, dst, **kw):
        self.history.add(dst)
        self.arrived = now()

    def process(self, *a, **kw):
        """null iterator"""
        if False:
            yield None # never executes, but converts function to generator
        raise StopIteration

    #def __del__(self):
    #    self.log("collected")
