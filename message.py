import itertools
import logging

from SimPy.Simulation import *

from util import LogProxy

_msg_counter = itertools.count()

class Message(Process):

    def __init__(self, model, **kw):

        # clone msg id if passed
        self.msgid = kw.pop('msgid', None)
        if not self.msgid:
            self.msgid = _msg_counter.next()

        super(Message, self).__init__(name="Message %d" % self.msgid)

        # preserve msg history
        self.history = kw.get('history', set())

        self.model = model

    def logger(self, src, dst):
        def log(msg):
            print "n%-3s : m%-3s : %s" % (dst.id, self.msgid, msg)
        return log

    def send(self, src, dst, **kw):
        self.history.add(dst)
        log = self.logger(src, dst)

        if src != None:
            latency = self.model.latency(src, dst)
            yield hold, self, latency
            log("arrived from %s" % src)
        else:
            pass
            log("arrived from source")


        if self.msgid in dst.server.msg_history:
            # TODO collect dropped stats
            log("already seen, dropping")
            raise StopIteration
        else:
            log("adding to server history")
            dst.server.msg_history.append(self.msgid)

        # wait for the processor, recording waiting stats
        yield request, self, dst.server.processor

        log("got processor")

        # simulate the work
        yield hold, self, dst.server.service_time()

        log("processing")

        # do our work, sending any messages
        #for msg in self.process(src, dst, log, **kw):
        #    activate(*msg)
        self.process(src, dst, log, **kw)

        # release the processor
        yield release, self, dst.server.processor
        log("finished")


    def process(self, *a, **kw):
        pass
        #if False:
        #    yield None # never executes, but converts function to generator
        #raise StopIteration

    def __str__(self):
        return "message %d" % self.msgid

    #def __del__(self):
    #    self.log("collected")
