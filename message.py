import itertools
import logging

from SimPy.Simulation import *

from util import LogProxy

_msg_counter = itertools.count()

class Message(Process):

    def __init__(self, model, **kw):
        # clone msg id if passed
        self.msgid = kw.pop('msgid', None)
        self.history = kw.get('history', set())
        if not self.msgid:
            self.msgid = _msg_counter.next()
        self.model = model
        self.log = LogProxy(self)
        super(Message, self).__init__(name="Message %d" % self.msgid)

    def send(self, src, dst, **kw):
        self.init(src, dst, **kw)
        self.log.info("%s started" % self)

        if src != None:
            src.log.info("sending %s from %s to %s" % (self, src, dst))
            latency = self.model.nodes.link_latency(src, dst)
            yield hold, self, latency
            dst.log.info("%s arrived at %s from %s" % (self, dst, src))
        else:
            pass
            dst.log.info("%s arrived from source" % self)


        if self.msgid in dst.server.msg_history:
            # TODO collect dropped stats
            dst.server.log.info("already seen message, dropping")
            raise StopIteration
        else:
            dst.server.log.info("adding message %d to history" % self.msgid)
            dst.server.msg_history.append(self.msgid)

        # wait for the processor, recording waiting stats
        yield request, self, dst.server.processor

        self.log.info("%s got processor on %s" % (self, dst))

        # simulate the work
        yield hold, self, dst.server.service()

        self.log.info("%s processing" % self)

        # do our work, sending any messages
        for msg in self.process(src, dst, **kw):
            activate(*msg)

        # release the processor
        yield release, self, dst.server.processor
        self.log.info("%s finished" % self)

    def init(self, src, dst, **kw):
        self.history.add(dst)
        self.arrived = now()

    def process(self, *a, **kw):
        """null iterator"""
        if False:
            yield None # never executes, but converts function to generator
        raise StopIteration

    def __str__(self):
        return "message %d" % self.msgid

    #def __del__(self):
    #    self.log("collected")
