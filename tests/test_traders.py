from ..market import Bid, Ask, MarketRules
from ..traders import ZIP, Buyer, Seller
from ..grid import Job

j = Job(10, 10)
market = MarketRules
market.min = 1
market.max = 100

def test_zip_buyer_better_bid_failure():
    b = Buyer(ZIP, 100, market)
    init = b.price
    b.observe(Bid(b, None, j, init *0.8), False)
    assert b.price > init

def test_zip_buyer_worse_bid_failure():
    b = Buyer(ZIP, 100, market)
    init = b.price
    b.observe(Bid(b, None, j, init*1.2), False)
    assert b.price == init

def test_zip_buyer_better_bid_succeed():
    b = Buyer(ZIP, 100, market)
    init = b.price
    b.observe(Bid(b, None, j, init * 0.8), True)
    assert b.price < init

def test_zip_buyer_worse_bid_succeed():
    b = Buyer(ZIP, 100, market)
    init = b.price
    b.observe(Bid(b, None, j, init * 1.2), True)
    assert b.price == init

def test_zip_buyer_better_ask_failure():
    b = Buyer(ZIP, 100, market)
    init = b.price
    b.observe(Ask(b, None, j, init * 0.8), False)
    assert b.price == init

def test_zip_buyer_worse_ask_failure():
    b = Buyer(ZIP, 100, market)
    init = b.price
    b.observe(Ask(b, None, j, init * 1.2), False)
    assert b.price == init

def test_zip_buyer_better_ask_succeed():
    b = Buyer(ZIP, 100, market)
    init = b.price
    b.observe(Ask(b, None, j, init * 0.8), True)
    assert b.price < init

def test_zip_buyer_worse_ask_succeed():
    b = Buyer(ZIP, 100, market)
    init = b.price
    print b.price
    b.observe(Ask(b, None, j, init * 1.2), True)
    assert b.price > init

# seller
def test_zip_seller_better_bid_failure():
    b = Seller(ZIP, 100, market)
    init = b.price
    print init
    b.observe(Bid(b, None, j, init * 1.2 ), False)
    assert b.price == init

def test_zip_seller_worse_bid_failure():
    b = Seller(ZIP, 100, market)
    init = b.price
    b.observe(Bid(b, None, j, init * 0.8), False)
    assert b.price == init

def test_zip_seller_better_bid_succeed():
    b = Seller(ZIP, 100, market)
    init = b.price
    b.observe(Bid(b, None, j, init * 1.2), True)
    assert b.price > init

def test_zip_seller_worse_bid_succeed():
    b = Seller(ZIP, 100, market)
    init = b.price
    b.observe(Bid(b, None, j, init * 0.8), True)
    assert b.price < init

def test_zip_seller_better_ask_failure():
    b = Seller(ZIP, 100, market)
    init = b.price
    b.observe(Ask(b, None, j, init * 1.2), False)
    assert b.price < init

def test_zip_seller_worse_ask_failure():
    b = Seller(ZIP, 100, market)
    init = b.price
    b.observe(Ask(b, None, j, init * 0.8), False)
    assert b.price == init

def test_zip_seller_better_ask_succeed():
    b = Seller(ZIP, 100, market)
    init = b.price
    b.observe(Ask(b, None, j, init * 1.2), True)
    assert b.price > init

def test_zip_seller_worse_ask_succeed():
    b = Seller(ZIP, 100, market)
    init = b.price
    b.observe(Ask(b, None, j, init * 0.8), True)
    assert b.price == init

