from SimPy.Simulation import now

enabled = True

class Tracer(object):

    def __init__(self, node, messages=[]):
        self.messages = messages
        self.node_msg = 'n%-5d' % node.id
        self.node = node

    def add(self, msg):
        return Tracer(self.node, self.messages + [msg])
        
    def __call__(self, msg):
        print " : ".join(['%-10.3f' % now(), self.node_msg] +
                         self.messages + 
                         [msg])

    def __nonzero__(self):
        global enabled
        return enabled

