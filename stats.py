from random import *

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
        return norm

    @staticmethod
    def expon(mean):
        lmda = 1.0/mean
        return lambda: expovariate(lmda)

    @staticmethod
    def gamma(mean, shape=2):
        return lambda: gammavariate(shape, mean)

    @staticmethod
    def uniform(a, b):
        return lambda: uniform(a, b)

    @staticmethod
    def uniform_int(a, b):
        return lambda: randint(a, b)


def list_mean(items, attr):
    return sum(getattr(i, attr) for i in items) / float(len(items))

def mean_server_utilisation(model):
    return list_mean(model.nodes, 'mean_utilisation')

def mean_queue_time(model):
    return list_mean(model.nodes, 'mean_queue_wait')
