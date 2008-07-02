from random import *

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
    def gamma(mean, shape=2):
        x = lambda: gammavariate(shape, mean)
        x.mean = mean
        return x

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
    return sum(getter(i) for i in items) / float(len(items))

def mean_server_utilisation(model):
    return list_mean(model.nodes, lambda x: x.server.mean_utilisation)

def mean_queue_time(model):
    return list_mean(model.nodes, lambda x: x.server.mean_queue_wait)

def mean_resource_util(model):
    return list_mean(model.nodes, lambda x: x.resource.utilisation)

# supply/demand calculations


