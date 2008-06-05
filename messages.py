from message import Message

class BroadcastMessage(Message):
    """Simple Message that has a TTL and sends itself on to all nodes
    until the TTL expires"""
    def process(self, src, dst, log, **kw):
        dst.shout_msg(self, **kw)




