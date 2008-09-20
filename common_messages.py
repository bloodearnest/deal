from SimPy.Simulation import reactivate
from message import Message

# point to point message
class NegotiationMessage(Message):
    def __init__(self, source, target, proposal):
        self.source = source
        self.target = target
        self.proposal = proposal # can be a quote or aoolc or whatever
        super(NegotiationMessage, self).__init__()


def check_target(node, target, trace):
    if node.resource_agent is target:
        return target
    elif node.confirm_job_agent(target, trace):
        return target
    else:
        trace("WARNING: %s not found at %s" % (target, node))
    return None


# accept process messages, simple really
class Accept(NegotiationMessage):
    """Accept sent to seller"""
    def process(self, src, dst, trace, **kw):
        target = check_target(dst, self.target, trace)
        if target:
            target.accept(self.proposal)

class Reject(NegotiationMessage):
    """Rejection of acceptance, sent to buyer"""
    def process(self, src, dst, trace, **kw):
        target = check_target(dst, self.target, trace)
        if target:
            target.reject(self.proposal)

# confirm process
class Confirm(NegotiationMessage):
    """Confirmation of acceptance, sent to buyer"""
    def process(self, src, dst, trace, **kw):
        target = check_target(dst, self.target, trace)
        if target:
            target.confirm(self.proposal)

class Cancel(NegotiationMessage):
    """Cancellation of previous accept message, sent to seller"""
    def process(self, src, dst, trace, **kw):
        target = check_target(dst, self.target, trace)
        if target:
            target.cancel(self.proposal)

