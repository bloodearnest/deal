import itertools
import copy
from trace import Tracer

from SimPy.Simulation import *

_msg_counter = itertools.count()

class Message(Process):

    def __init__(self, **kw):

        # clone msg id if passed
        self.msgid = kw.pop('msgid', None)
        if not self.msgid:
            self.msgid = _msg_counter.next()

        super(Message, self).__init__(name="Message %d" % self.msgid)

        # preserve msg history
        self.history = kw.get('history', set())

    def send_msg(self, *a, **kw):
        self.start(self.send(*a, **kw))

    def send(self, src, dst, **kw):
        self.history.add(dst)
        trace = Tracer(dst).add('m%-11d' % self.msgid)

        if src != None:
            latency = src.generate_latency(dst)
            yield hold, self, latency
            if trace: trace("arrived from %s" % src)
        else:
            pass
            if trace: trace("arrived from source")


        if self.msgid in dst.server.msg_history:
            # TODO collect dropped stats
            if trace: trace("already seen, dropping")
            raise StopIteration
        else:
            if trace: trace("adding to server history")
            dst.server.msg_history.append(self.msgid)

        # wait for the processor, recording waiting stats
        yield request, self, dst.server.processor

        if trace: trace("got processor")

        # simulate the work
        yield hold, self, dst.server.service_time()

        if trace: trace("processing")

        # do our work
        self.process(src, dst, trace, **kw)

        # release the processor
        yield release, self, dst.server.processor
        if trace: trace("finished")

    def process(self, *a, **kw):
        pass

    def clone(self):
        # copy across all data
        cp = copy.copy(self)
        # reset SimPy machinery
        Process.__init__(cp, name=self.name)
        return cp

    def __str__(self):
        return "message %d" % self.msgid

    #def __del__(self):
    #    print "msg %d collected" % self.msgid


class MessageWithQuote(Message):
    def __init__(self, quote, *a, **kw):
        super(MessageWithQuote, self).__init__(*a, **kw)
        self.quote = quote

    def record(self, node):
        self.quote.job.nodes_visited.add(node.id)

    def check_buyer(self, dst, trace):
        buyer = self.quote.buyer
        trace = trace.add("j%-5s" % self.quote.job.id)
        if buyer in dst.buyers and buyer.active:
            return buyer
        elif buyer.id in dst.buyer_ids:
            trace and trace("buyer has migrated")
        else:
            trace("WARNING: %s is not and has never been at %s" % (buyer, dst))
        return None





