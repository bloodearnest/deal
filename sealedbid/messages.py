from SimPy.Simulation import reactivate
from message import MessageWithQuote
from common_messages import *

# listen process messages
class Advert(MessageWithQuote):
    """Advert sent to seller"""
    def process(self, src, dst, trace, **kw):
        self.quote.job.nodes_visited.add(dst.id)
        # pass it on 
        ttl = kw.get('ttl', 1)
        dst.shout_msg(self, ttl=ttl)
        dst.resource_agent.quote(self.quote)


class PrivateQuote(MessageWithQuote):
    """quote sent to buyer"""
    def process(self, src, dst, trace, **kw):
        buyer = dst.confirm_job_agent(self.quote.buyer, trace)
        if buyer and buyer.active:
            buyer.quote(self.quote)


