from trace import BaseTracer
from common_messages import *
from common_processes import *

from SimPy.Simulation import now

class JobAgent(object):
    def __init__(self, job):
        self.start_time = now()
        self.job = job
        self.id = job.id
        self.accept_process = None
        self.confirm_process = None
        self.listen_process = None
        self.trace = BaseTracer()

        self.rejected = set()
        self.cancelled = set()
        self.timedout = set()

    def start_accept_process(self, other, value, timeout):
        accept = Accept(self, other, value)
        accept.send_msg(self.node, other.node)
        self.accept_process = AcceptProcess(self, value, timeout)
        self.accept_process.start(self.accept_process.accept())

    # clean up
    def cancel_all(self):
        if self.listen_process:
            cancel_process(self.listen_process)
        if self.accept_process:
            cancel_process(self.accept_process)
        if self.confirm_process:
            cancel_process(self.confirm_process)


    # public AcceptProcess message interface
    # buyers only ever have one accept process
    def confirm(self, confirm):
        if self.accept_process:
            self.accept_process.signal("confirm", confirm)
        else:
            self.trace("WARNING: no accept process to receive confirm")

    def reject(self, reject):
        if self.accept_process: 
            self.accept_process.signal("reject", reject)
        else:
            self.trace("WARNING: no accept process to receive reject")

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


class ResourceAgent(object):

    def __init__(self, node):
        self.node = node
        self.id = node.id
        self.trace = BaseTracer()

        # sellers are trading on multiple jobs
        self.accept_processes = {}
        self.confirm_processes = {}
        self.rejected = set()
        self.cancelled = set()

    @property
    def resource(self):
        return self.node.resource

    # utility functions
    def confirm_and_start_job(self, job, other, value):
        # sending confirmation message
        confirm = Confirm(self, other, value)
        confirm.send_msg(self.node, other.node)
        
        # start procsses to listen for cancellations
        confirm_process = ConfirmProcess(self, value)
        activate(confirm_process, confirm_process.confirm())
        self.confirm_processes[job.id] = confirm_process

        # start the job
        self.resource.start(job, confirm_process)

    
    def send_reject(self, other, value):
        reject = Reject(self, other, value)
        reject.send_msg(self.node, other.node)


    # public AcceptProcess message interface
    def confirm(self, confirm):
        if confirm.id in self.accept_processes:
            process = self.accept_processes[confirm.id]
            process.signal("confirm", confirm)
        else:
            self.trace("WARNING: no accept process for confirm %s" 
                    % reject.str(self))
    
    def reject(self, reject):
        if reject.id in self.accept_processes:
            process = self.accept_processes[reject.id]
            process.signal("reject", reject)
        else:
            self.trace("WARNING: no accept process for reject %s" 
                    % reject.str(self))

 
    # public ConfirmProcess message interface
    def cancel(self, cancel):
        trace = self.trace.add("j%-5s" % cancel.id)
        self.cancelled.add(cancel.id)
        if cancel.id in self.confirm_processes:
            process = self.confirm_processes[cancel.id]
            process.signal("cancel", cancel)
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


    #internal ConfirmProcess interface
    # this should be the same for all resource agents
    def cancel_received(self, cancel):
        trace = self.trace.add('j%-5s' % cancel.job)

        if cancel.job in self.resource.jobs:
            trace and trace("got cancel, cancelling job %s" 
                    % cancel.job.id)
            self.resource.cancel(cancel.job);
            del self.confirm_processes[cancel.job.id]
        else:
            trace("WARNING: got cancel for job not running (%s)"
                    % cancel.job.id)

    def complete_received(self, complete):
        trace = self.trace.add('j%-5s' % complete.job.id)
        trace and trace("job %s completed, cleaning up" 
                % complete.job.id)
        del self.confirm_processes[complete.job.id]


