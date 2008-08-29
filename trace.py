from SimPy.Simulation import now

enabled = True

class BaseTracer(object):

    def __init__(self, messages=None):
        if messages is None:
            self.messages = []
        else:
            self.messages = messages
    
    def add(self, msg):
        return BaseTracer(self.messages + [msg])

    def __call__(self, msg):
        print " : ".join(['%-8.5f' % now()] + self.messages + [msg])

    def __nonzero__(self):
        global enabled
        return enabled

class Tracer(BaseTracer):
    def __init__(self, node, messages=None):
        super(Tracer, self).__init__(messages)
        self.node_msg = 'n%-5d' % node.id
        self.messages.append(self.node_msg)

        

