from SimPy.Simulation import now
from trace import Tracer
from processes import *
from trader import Trader


class Seller(Trader):
    def __init__(self, id, rationale, node, **kw):
        Trader.__init__(self, id, rationale, **kw)
        self.node = node
        self.trace = Tracer(node)
        self.trace = self.trace.add('%-12s' % self)
        self.listen_process = None

        # sellers are trading on multiple jobs
        self.accept_processes = {}
        self.confirm_processes = {}

        self.rejected = set()
        self.cancelled = set()
    
    @property
    def resource(self):
        return self.node.resource

    def start(self):
        self.listen_process = ListenProcess(self)
        activate(self.listen_process, self.listen_process.listen())
  
    # public AcceptProcess message interface
    def confirm(self, confirm):
        if confirm.id in self.accept_processes:
            process = self.accept_processes[confirm.id]
            process.signal("confirm", confirm)
        else:
            self.trace("WARNING: no accept process for confirm %s" 
                    % reject.str(self.trader))
    
    def reject(self, reject):
        if reject.id in self.accept_processes:
            process = self.accept_processes[reject.id]
            process.signal("reject", reject)
        else:
            self.trace("WARNING: no accept process for reject %s" 
                    % reject.str(self.trader))

 
    # public ConfirmProcess message interface
    def cancel(self, cancel):
        trace = self.trace.add("j%-5s" % cancel.id)
        self.cancelled.add(cancel)
        if cancel.id in self.confirm_processes:
            process = self.confirm_processes[cancel.id]
            process.signal("cancel", cancel)
        elif cancel.id in self.rejected:
            trace and trace("got cancel for job already rejected")
        else:
            trace and trace("no confirm process for cancel, "
                    "probably out of sync")
    
    def complete(self, complete):
        trace = self.trace.add("j%-5s" % cancel.id)
        if complete.id in self.confirm_processes:
            process = self.confirm_processes[complete.id]
            process.signal("complete", complete)
        else:
            trace("WARNING: no confirm process for complete")


    # utility function
    def create_quote(self):
        self.price = self.rationale.quote()
        return Ask(None, self, self.resource.free, self.price)

    def create_accept(self, quote):
        return Ask(quote.buyer, self, quote.job, quote.price)

    def viable_quote(self, q):
        return (self.active and
                self.bid and
                q.price >= self.price and
                q.size <= self.node.resource.free)


