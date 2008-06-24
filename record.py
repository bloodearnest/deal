import math
import pylab
from SimPy.Simulation import now

buys = []
buys_theory = []
sells = []
sells_theory = []

failed = []

def trade(quote, success):
    t = now()
    if success:
        trade = (quote.price, quote.quantity, t)
        #print quote.price, quote.seller.limit, quote.buyer.limit 
        buys.append(trade)
        sells.append(trade)

    else:
        failed.append((quote.buyer.limit, quote.job.size))

def equilibrium(buys, sells, name):
    
    PRICE = 0
    QUANT = 1
    TIME = 2
    eq_price = 0
    eq_time = 0
    surplus = 0

    buys.sort()
    sells.sort()
    buys.reverse()

    # do we cross over?
    if (sells[0][PRICE] <= buys[0][PRICE]):

        found = False
        bfinished = sfinished = False

        bindex = 0
        sindex = 0
        buy = buys[bindex]
        sell = sells[sindex]
        last_buy = last_sell = None

        x = last_buy_price = last_sell_price = 0
        xs = [0,0]
        dy = []
        sy = []

        while bindex < len(buys) and sindex < len(sells):

            if sell[QUANT] == buy[QUANT]:
                quantity = sell[QUANT]
            else:
                quantity = math.fabs(sell[QUANT] - buy[QUANT])

            # plotting 
            x += quantity
            xs += [x, x]
            sy += [last_sell_price, sell[PRICE]]
            last_sell_price = sell[PRICE]
            dy += [last_buy_price, buy[PRICE]]
            last_buy_price = buy[PRICE]

            # stats
            profit = (buy[PRICE] - sell[PRICE]) * quantity
            bfinished = bindex + 1 == len(buys)
            sfinished = sindex + 1 == len(sells)

            if not found:

                if (sell[PRICE] > buy[PRICE]):
                    # we have crossed the equilibrium point
                    eq_price = (last_buy[PRICE] + last_sell[PRICE]) / 2.0
                    eq_time = last_buy[TIME]
                    found = True

                elif sindex + 2 == len(sells):
                    # no more sells
                    eq_price = (buy[PRICE] + buys[bindex+1][0]) / 2.0
                    eq_time = buy[TIME]
                    surplus += profit
                    found = True
                    sindex = len(sells)
                    
                elif bindex + 2 == len(buys):
                    # no more buys
                    eq_price = (sell[PRICE] + sells[sindex+1][0]) / 2.0
                    eq_time = sell[TIME]
                    surplus += profit
                    found = True
                    bindex = len(buys)

                else:
                    surplus += profit

            # move along according to quantity
            if buy[QUANT] > sell[QUANT]:
                buy = (buy[PRICE], buy[QUANT] - quantity, buy[TIME])
                sindex += 1
                last_sell = sell
                if sindex < len(sells):
                    sell = sells[sindex]
            elif buy[QUANT] < sell[QUANT]:
                sell = (sell[PRICE], sell[QUANT] - quantity, sell[TIME])
                bindex += 1
                last_buy = buy
                if bindex < len(buys):
                    buy = buys[bindex]
            else:
                last_buy = buy
                last_sell = sell
                bindex += 1
                sindex += 1
                buy = buys[bindex]
                sell = sells[sindex]

        ms = min(len(xs), len(sy))
        md = min(len(xs), len(dy))
        pylab.clf()
        pylab.plot(xs[:ms], sy[:ms])
        pylab.plot(xs[:md], dy[:md])
        pylab.savefig(name)

    return eq_price, surplus, eq_time



def report():
    real = equilibrium(buys, sells, "real.png")
    theory = equilibrium(buys_theory, sells_theory, "theory.png")

    alpha = real[0] / theory[0]
    eff = real[1] / theory[1] * 100

    print "efficiency: %.2f%%" % eff






