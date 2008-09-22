def pqcurve_iter(buys, sells):
    
    # use static default mutable arg hack, since
    # it seems that generators can't be closures!
    def trade_iter(trades, n_done=[]):
        for t in trades:
            yield t
        #yield t
        n_done.append(0)
        if len(n_done) < 2:
            while 1:
                yield None, None, None

    buys = trade_iter(buys)
    sells = trade_iter(sells)

    bp, bq, bt = buys.next()
    sp, sq, st = sells.next()

    if sp > bp: # no intersect
        raise StopIteration
    else:
        while 1:
            
            if sp and bq > sq:
                point = bp, sp, sq, bt, st
                bq -= sq
                sp, sq, st = sells.next()
            
            elif bp and bq < sq:
                point = bp, sp, bq, bt, st
                sq -= bq
                bp, bq, bt = buys.next()

            else: #sq == bq
                point = bp, sp, max(bq, sq), bt, st
                bp, bq, bt = buys.next()
                sp, sq, st = sells.next()

            yield point
        


def find_equilibrium(buys, sells):
    
    eq_price = 0
    eq_time = 0
    surplus = 0

    found = False
    sell_prices = [0,0]
    buy_prices = [0,0]
    last_bt = last_st = 0

    for buy, sell, q, bt, st in pqcurve_iter(buys, sells):

        if buy is None and sell is None:
            eq_price = (buy_prices[1] + sell_prices[1]) / 2.0
            eq_time = last_bt
            break

        elif buy is None:
            # reached end of buys
            eq_price = (sell_prices[1] + buy_prices[0]) / 2.0
            eq_time = max(last_st, last_bt)
            break

        elif sell is None:
            # reached end of sells
            eq_price = (sell_prices[0] + buy_prices[1]) / 2.0
            eq_time = max(last_st, last_bt)
            break

        elif sell > buy:
            # we have crossed the equilibrium point
            eq_price = (buy_prices[1] + sell_prices[1]) / 2.0
            eq_time = max(last_st, last_bt)
            break

        else:
            profit = (buy - sell) * q
            surplus += profit
            sell_prices.pop(0)
            sell_prices.append(sell)
            buy_prices.pop(0)
            buy_prices.append(buy)
            last_bt = bt
            last_st = st

    if not eq_price:
        eq_price = (buy + sell) / 2.0
        eq_time = max(bt, st)

    return eq_price, surplus, eq_time


