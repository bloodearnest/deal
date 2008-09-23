from itertools import chain
from random import *
import scipy.stats
from SimPy.Simulation import now

def random_other(seq, this):
    other = choice(seq)
    while other == this:
        other = choice(seq)
    return other

class dists(object):

    @staticmethod
    def normal(mean, sigma=None):
        if sigma is None:
            sigma = mean/4.0 # default shape
        def norm():
            x = normalvariate(mean, sigma)
            while (x <= 0):
                x = normalvariate(mean, sigma)
            return x
        norm.mean = mean
        return norm


    @staticmethod
    def normal_int(mean, sigma=None):
        norm = dists.normal(mean, sigma)
        x = lambda : int(norm())
        x.mean = mean
        return x


    @staticmethod
    def expon(mean):
        lmda = 1.0/mean
        x = lambda: expovariate(lmda)
        x.mean = mean
        return x

    @staticmethod
    def gamma(mean, shape):
        alpha = mean / float(shape)
        x = lambda: gammavariate(alpha, shape)
        x.mean = mean
        return x

    @staticmethod
    def shaped_gamma(shape):
        def _gamma(mean):
            return dists.gamma(mean, shape)
        return _gamma

    @staticmethod
    def uniform(a, b):
        x = lambda: uniform(a, b)
        x.mean = (b - a) / 2
        return x


    @staticmethod
    def uniform_int(a, b):
        x = lambda: randint(a, b)
        x.mean = (b - a) / 2
        return x

    @staticmethod
    def constant(i):
        x = lambda: i
        x.mean = i
        return x


# general stat calculation functions
def list_mean(items, getter):
    if items:
        return sum(getter(i) for i in items) / float(len(items))
    else:
        return 0

def tseries_slice(monitor, t1, t2):
    tseries = []
    lasty = 0 

    it = iter(monitor)

    for t,y in it:
        if t >= t1:
            tseries.append((t1,lasty))
            break
        else:
            lasty = y

    next = chain([(t,y)], it)
    for t,y in next:
        if t >= t2:
            break
        else:
            tseries.append((t,y))
            lasty = y
    tseries.append((t2,lasty))

    return tseries

def time_average(seq):
    sum = 0
    lastt, lasty = seq[0]
    for t,y in seq[1:]:
        sum += (t - lastt) * lasty
        lastt, lasty = t,y
    return sum / float(seq[-1][0] - seq[0][0])

def timeslice_average(mon, t1, t2=None):
    if not mon:
        return 0
    elif len(mon) == 1:
        return mon.timeAverage()
    if t2 is None:
        t2 = now()
    seq = tseries_slice(mon, t1, t2)
    return time_average(seq)


def mean_resource_util(model):
    return list_mean(model.nodes, lambda x: x.resource.utilisation)
def mean_server_util(model):
    return list_mean(model.nodes, lambda x: x.server.mean_utilisation)
def mean_queue_time(model):
    return list_mean(model.nodes, lambda x: x.server.mean_queue_wait)

def current_grid_util(model, tlast):
    return list_mean(model.nodes, lambda x: x.resource.current_util(tlast))
def current_server_util(model, tlast):
    return list_mean(model.nodes, lambda x: x.server.current_util(tlast))
def current_server_queue(model, tlast):
    return list_mean(model.nodes, lambda x: x.server.current_queue(tlast))

def mean_broker_server_util(model):
    return list_mean(model.brokers.values(), lambda x: x.node.server.mean_utilisation)
def mean_broker_queue_time(model):
    return list_mean(model.brokers.values(), lambda x: x.node.server.mean_queue_wait)

def current_broker_util(model, tlast):
    return list_mean(model.brokers.values(), lambda x: x.node.server.current_util(tlast))
def current_broker_queue(model, tlast):
    return list_mean(model.brokers.values(), lambda x: x.node.server.current_queue(tlast))

def skew(mon):
    return scipy.stats.skew([n[1] for n in mon])
