from ..market import Bid, Ask, MarketRules
from ..traders import ZIP, Buyer, Seller
from ..grid import Job

j = Job(10, 10)
market = MarketRules
market.min = 1
market.max = 100

def test_zip_buyer_lower_bid_nodeal():
    b = Buyer(ZIP, 75, market)
    init = b.price
    b.observe(Bid(b, None, j, 40), False)
    assert b.price > init

def test_zip_buyer_higher_bid_nodeal():
    b = Buyer(ZIP, 75, market)
    init = b.price
    b.observe(Bid(b, None, j, 70), False)
    assert b.price == init

def test_zip_buyer_lower_bid_deal():
    b = Buyer(ZIP, 75, market)
    init = b.price
    b.observe(Bid(b, None, j, 40), True)
    assert b.price < init

def test_zip_buyer_higher_bid_deal():
    b = Buyer(ZIP, 75, market)
    init = b.price
    b.observe(Bid(b, None, j, 70), True)
    assert b.price == init

def test_zip_buyer_lower_ask_nodeal():
    b = Buyer(ZIP, 75, market)
    init = b.price
    b.observe(Ask(b, None, j, 40), False)
    assert b.price == init

def test_zip_buyer_higher_ask_nodeal():
    b = Buyer(ZIP, 75, market)
    init = b.price
    b.observe(Ask(b, None, j, 70), False)
    assert b.price == init

def test_zip_buyer_lower_ask_deal():
    b = Buyer(ZIP, 75, market)
    init = b.price
    b.observe(Ask(b, None, j, 40), True)
    assert b.price < init

def test_zip_buyer_higher_ask_deal():
    b = Buyer(ZIP, 75, market)
    init = b.price
    print b.price
    b.observe(Ask(b, None, j, 70), True)
    assert b.price > init

