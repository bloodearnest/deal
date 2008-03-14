from message import Message

class BroadcastMessage(Message):
    """Simple Message that has a TTL and sends itself on to all nodes
    until the TTL expires"""

    def process(self, src, dst, log, **kw):
        ttl = kw.pop('ttl', 3)
        if ttl:
            # send same message on
            ttl -= 1
            sent_some = False
            old_history = self.history
            new_history = old_history.union(dst.neighbors)

            for link in dst.neighbors:
                if link not in old_history: # not already seen
                    sent_some = True
                    log("passing on to %s (ttl %d)" % (link, ttl))
                    msg = BroadcastMessage(self.model,
                                           msgid=self.msgid,
                                           history=new_history)
                    msg.start(msg.send(dst, link, ttl=ttl))
                else:
                    log("ttl %d, %s in history, not passing on" % (ttl, link))
            if not sent_some:
                log("message received everywhere before ttl expired")
        else:
            log("TTL expired")


#class Shout(Message):
#    def process(self, src, dst, log, quote, **kw):
#
#        if quote.bid:
#            ask = dst.seller.consider(quote)
#            if ask:
#                shout = Shout(self.model)
