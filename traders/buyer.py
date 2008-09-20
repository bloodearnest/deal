from SimPy.Simulation import activate, now
from trace import Tracer
from trader import Trader
from processes import *

class Buyer(Trader):

    def __init__(self, id, rationale, job, **kw):
        Trader.__init__(self, id, rationale, **kw)
        self.job = job
        self.migrations = 0
        self.listen_process = None

        self.accepted = set()
        # buyers only have a single accept/confirm   
        self.accept_process = None
        self.confirm_process = None

    def start(self):
        self.start_time = now()
        self.node.job_agents.add(self)
        self.listen_process = ListenProcess(self)
        activate(self.listen_process, self.listen_process.listen())
    
    def start_on_node(self, node):
        self.node = node
        self.regions.add(self.node.region)
        self.trace = Tracer(node)
        self.trace = self.trace.add('%-12s' % self)
        self.trace = self.trace.add('j%-5d' % self.job.id)
        self.trace and self.trace("starting on %s" % node)
        self.start()


    # clean up
    def cancel_all(self):
        if self.listen_process:
            cancel_process(self.listen_process)
        if self.accept_process:
            cancel_process(self.accept_process)
        if self.confirm_process:
            cancel_process(self.confirm_process)

    # buyer mobility utilities
    def remove_from_node(self):
        self.trace and self.trace("removing from %s" % self.node)
        self.node.job_agents.remove(self)
        self.node.old_job_agents.add(self)

    def migrate(self):
        self.trace and self.trace("migrating")
        
        current = self.node
        self.remove_from_node()
        
        r = self.node.graph.regions
        max = r[0] * r[1]

        if len(self.regions) == max:
            self.regions = set()
            others = self.node.graph.nodes()
        else:
            # choose another node in a different region
            others = [n for n in self.node.graph.nodes_iter() 
                      if n.region not in self.regions]

        other = random.choice(others)
        while other == current:
            other = random.choice(others)
        
        #cancel any events (there shouldn't be, but just in case)
        self.cancel_all()

        self.trace and self.trace("moving to %s" % other)
        self.start_on_node(other)
  
    def finish_trading(self):
        self.remove_from_node()
        self.active = False
    
    # public AcceptProcess message interface
    # buyers only ever have one accept process
    def confirm(self, confirm):
        if self.accept_process:
            self.accept_process.signal("confirm", confirm)
        elif confirm in self.accepted:
            self.trace and self.trace("no accept process active, but has been accepted")
        else:
            self.trace("WARNING: no accept process to receive confirm")

    def reject(self, reject):
        if self.accept_process: 
            self.accept_process.signal("reject", reject)
        else:
            self.trace("WARNING: no accept_process to receive reject")

    # public ConfirmProcess message interface
    # buyers only ever have one confirm process
    def cancel(self, cancel):
        if self.confirm_process:
            self.confirm_process.signal("cancel", cancel)
        else:
            self.trace("WARNING: no confirm_process to receive cancel")

    def complete(self, complete):
        if self.confirm_process:
            self.confirm_process.signal("complete", complete)
        else:
            self.trace("WARNING: no confirm_process to receive complete")

    # utility functions
    def create_quote(self):
        self.price = self.rationale.quote()
        return Bid(self, None, self.job, self.price)

    def create_accept(self, quote):
        return Bid(self, quote.seller, self.job, quote.price)

    def viable_quote(self, q):
        return (self.active and 
                q.ask and 
                q.price <= self.price and 
                q.size >= self.job.size)

