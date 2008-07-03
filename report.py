import pylab
import stats
import record
from draw import plot_eq
import equilibrium

def grid(model):

    print "Grid:"
    print " - resource util: %.2f%%" % (stats.mean_resource_util(model) * 100)
    print " - server util:   %.2f%%" % (stats.mean_server_utilisation(model) * 100)
    print " - queue time:    %.2fs"  % stats.mean_queue_time(model)

    failed = record.failures.count / float(record.njobs) * 100
    print " - failed: %.2f%%" % failed
    record.failures.report()
    record.successes.report()

    for reason, count in record.failed.iteritems():
        print "Failed by %s: %.2f%%" % (reason, 
                                        count/float(record.failures.count)*100)


def economy(model):
    print "Economy:"

    # sort all trades
    record.buys.sort()
    record.buys.reverse()
    record.sells.sort()
    record.buys_theory.sort()
    record.buys_theory.reverse()
    record.sells_theory.sort()
    
    real = equilibrium.find_equilibrium(record.buys, record.sells)
    plot_eq(record.buys, record.sells)
    pylab.savefig("real.png")
    pylab.clf()
    
    theory = equilibrium.find_equilibrium(record.buys_theory, record.sells_theory)
    plot_eq(record.buys_theory, record.sells_theory)
    pylab.savefig("theory.png")
    
    #xs, ys = draw.smooth(trade_times, trade_prices, 20)
    #pylab.clf()
    #pylab.plot(xs, ys)
    #pylab.savefig("trades.png")

    #alpha = real[0] / theory[0]
    eff = real[1] / theory[1] * 100
    print "actual eq price: %d" % real[0]
    print "theory eq price: %d" % theory[0]
    print "efficiency: %.2f%%" % eff
    bu = record.buyer_util.mean()
    su = record.seller_util.mean()
    print "avg trader util: %d (buyer: %d, seller: %d)" % ((bu+su)/2.0,bu,su)
    print "avg buyer wait: %.2f" % record.buyer_timeouts.mean()
                  
