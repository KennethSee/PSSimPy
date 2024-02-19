import unittest

from PSSimPy.credit_facilities.simple_priced import SimplePriced
from PSSimPy.account import Account


class TestCreditFacility(unittest.TestCase):
    
    def setUp(self) -> None:
        self.cf_price_fixed = SimplePriced(price=15)
        self.cf_price_rate = SimplePriced(rate=0.1)
        self.cf_price_combined = SimplePriced(price=15, rate=0.1)
        self.a = Account("A", "Bank A", 100)
    
    def test_lend(self):
        # lend 100 credit to A, fee is fixed at 15
        self.cf_price_fixed.lend_credit(self.a, 100)
        self.assertEqual(self.cf_price_fixed.total_credit["A"], 100)
        self.assertEqual(self.cf_price_fixed.total_fee["A"], 15)
        self.assertEqual(self.cf_price_fixed.get_total_credit(self.a), 100)
        self.assertEqual(self.cf_price_fixed.get_total_fee(self.a), 15)
        self.assertEqual(self.a.balance, 200)

        # lend 100 credit to A, relative fee is 0.1 * 100 = 10
        self.cf_price_rate.lend_credit(self.a, 100)
        self.assertEqual(self.cf_price_rate.total_credit["A"], 100)
        self.assertEqual(self.cf_price_rate.total_fee["A"], 10)
        self.assertEqual(self.cf_price_rate.get_total_credit(self.a), 100)
        self.assertEqual(self.cf_price_rate.get_total_fee(self.a), 10)
        self.assertEqual(self.a.balance, 300)

        # lend 100 credit to A, total fee is 25 (fixed fee = 15 and relative fee = 10)
        self.cf_price_combined.lend_credit(self.a, 100)
        self.assertEqual(self.cf_price_combined.total_credit["A"], 100)
        self.assertEqual(self.cf_price_combined.total_fee["A"], 25)
        self.assertEqual(self.cf_price_combined.get_total_credit(self.a), 100)
        self.assertEqual(self.cf_price_combined.get_total_fee(self.a), 25)
        self.assertEqual(self.a.balance, 400)

        
    def test_collect(self):
        # lend 100 credit to A with 15 fixed fee, after repayment, balance is 100 - 15 = 85 
        self.cf_price_fixed.lend_credit(self.a, 100)
        self.cf_price_fixed.collect_repayment(self.a)
        self.assertEqual(self.cf_price_fixed.total_credit["A"], 0)
        self.assertEqual(self.cf_price_fixed.total_fee["A"], 0)
        self.assertEqual(self.cf_price_fixed.get_total_credit(self.a), 0)
        self.assertEqual(self.cf_price_fixed.get_total_fee(self.a), 0)
        self.assertEqual(self.a.balance, 85)
        
        # lend 100 credit to A with 10 relative fee, after repayment, balance is 85 - 10 = 75 
        self.cf_price_rate.lend_credit(self.a, 100)
        self.cf_price_rate.collect_repayment(self.a)
        self.assertEqual(self.cf_price_fixed.total_credit["A"], 0)
        self.assertEqual(self.cf_price_fixed.total_fee["A"], 0)
        self.assertEqual(self.cf_price_rate.get_total_credit(self.a), 0)
        self.assertEqual(self.cf_price_rate.get_total_fee(self.a), 0)
        self.assertEqual(self.a.balance, 75)
        
        # lend 100 credit to A with 15 fixed fee plus 10 relative fee, after repayment, balance is 85 - 15 - 10 = 50 
        self.cf_price_combined.lend_credit(self.a, 100)
        self.cf_price_combined.collect_repayment(self.a)
        self.assertEqual(self.cf_price_fixed.total_credit["A"], 0)
        self.assertEqual(self.cf_price_fixed.total_fee["A"], 0)
        self.assertEqual(self.cf_price_combined.get_total_credit(self.a), 0)
        self.assertEqual(self.cf_price_combined.get_total_fee(self.a), 0)
        self.assertEqual(self.a.balance, 50)