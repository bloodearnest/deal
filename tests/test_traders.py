from ..traders import ZIP, Buyer, Seller, Bid, Ask
from ..grid import Job

j = Job(10, 10)
def go(q, t, s) :
    for i in range(20):
        print t.price
        t.observe(q, s)
    print t.price


def test_zip_buyer_lower_bid_nodeal():
    b = Buyer(ZIP, 75, 1, 100)
    init = b.price
    b.observe(Bid(j, 40), False)
    assert b.price > init

def test_zip_buyer_higher_bid_nodeal():
    b = Buyer(ZIP, 75, 1, 100)
    init = b.price
    b.observe(Bid(j, 60), False)
    assert b.price == init

def test_zip_buyer_lower_bid_deal():
    b = Buyer(ZIP, 75, 1, 100)
    init = b.price
    b.observe(Bid(j, 40), True)
    assert b.price < init

def test_zip_buyer_higher_bid_deal():
    b = Buyer(ZIP, 75, 1, 100)
    init = b.price
    b.observe(Bid(j, 60), True)
    assert b.price == init

def test_zip_buyer_lower_ask_nodeal():
    b = Buyer(ZIP, 75, 1, 100)
    init = b.price
    b.observe(Ask(j, 40), False)
    assert b.price == init

def test_zip_buyer_higher_ask_nodeal():
    b = Buyer(ZIP, 75, 1, 100)
    init = b.price
    b.observe(Ask(j, 60), False)
    assert b.price == init

def test_zip_buyer_lower_ask_deal():
    b = Buyer(ZIP, 75, 1, 100)
    init = b.price
    b.observe(Ask(j, 40), True)
    assert b.price < init

def test_zip_buyer_higher_ask_deal():
    b = Buyer(ZIP, 75, 1, 100)
    init = b.price
    b.observe(Ask(j, 60), True)
    assert b.price > init

