from message import Message

class BroadcastMessage(Message):
    """Simple Message that has a TTL and sends itself on to all nodes
    until the TTL expires"""

    def process(self, src, dst, **kw):
        if self.ttl:
            # send sname message on
            ttl = self.ttl - 1
            sent_some = False
            old_history = self.history
            new_history = self.history.union(dst.links)

            for link in dst.links:
                if link not in old_history: # not already seen
                    sent_some = True
                    msg = BroadcastMessage(self.model, msgid=self.msgid,
                                     history=new_history)
                    self.log("ttl: %d, passed on to node %d" % (ttl, link.id))
                    yield msg, msg.send(dst, link, ttl=ttl)
                else:
                    self.log("ttl: %d, node %d in history, not passing on" %
                            (ttl, link.id))
            if not sent_some:
                self.log("message received everywhere before ttl expired")
        else:
            self.log("TTL expired")

    def init(self, *a, **kw):
        self.ttl = kw.pop('ttl', 3)
        super(BroadcastMessage, self).init(*a, **kw)



