import unittest

from PSSimPy.credit_facilities import SimpleCollateralized, SimplePriced
from PSSimPy.account import Account


class TestSimpleCollateralizedCreditFacility(unittest.TestCase):
    
    def setUp(self) -> None:
        self.a = Account("A", "Bank A", 100, posted_collateral=150)
        self.cf_collateralized = SimpleCollateralized()
    
    def test_lend(self):
        # lend 100 credit to A
        self.cf_collateralized.lend_credit(self.a, 100)
        self.assertEqual(self.cf_collateralized.get_total_credit(self.a), 100)
        self.assertEqual(self.cf_collateralized.get_total_fee(self.a), 0)
        self.assertEqual(self.a.balance, 200)

        # lend 100 credit to A, but failed due to insufficient collateral
        self.cf_collateralized.lend_credit(self.a, 100)
        self.assertEqual(self.cf_collateralized.get_total_credit(self.a), 100)
        self.assertEqual(self.cf_collateralized.get_total_fee(self.a), 0)
        self.assertEqual(self.a.balance, 200)

        
    def test_collect(self):
        pass
    
        # TODO use these tests after implementing EOD        
        # lend 100 credit to A, repaid with full amount
        self.cf_collateralized.lend_credit(self.a, 100)
        self.cf_collateralized.collect_repayment(self.a)
        self.assertEqual(self.cf_collateralized.get_total_credit(self.a), 0)
        self.assertEqual(self.cf_collateralized.get_total_fee(self.a), 0)
        self.assertEqual(self.a.balance, 200)
        
        # A has 100, lend 130 credit to A, A use 120, cannot repaid 20
        self.cf_collateralized.lend_credit(self.a, 100)
        self.cf_collateralized.lend_credit(self.a, 10)
        self.cf_collateralized.lend_credit(self.a, 15)
        self.cf_collateralized.lend_credit(self.a, 5)
        self.a.balance -= 120
        self.cf_collateralized.collect_repayment(self.a)
        self.assertEqual(self.cf_collateralized.get_total_credit(self.a), 0)
        self.assertEqual(self.cf_collateralized.get_total_fee(self.a), 0)
        self.assertEqual(self.a.posted_collateral, 150)



class TestSimplePricedCreditFacility(unittest.TestCase):
    
    def setUp(self) -> None:
        self.cf_price_fixed = SimplePriced(base_fee=15)
        self.cf_price_rate = SimplePriced(base_rate=0.1)
        self.cf_price_combined = SimplePriced(base_fee=15, base_rate=0.1)
        self.a = Account("A", "Bank A", 100)
    
    def test_lend(self):
        # lend 100 credit to A, fee is fixed at 15
        self.cf_price_fixed.lend_credit(self.a, 100)
        self.assertEqual(self.cf_price_fixed.get_total_credit(self.a), 100)
        self.assertEqual(self.cf_price_fixed.get_total_fee(self.a), 15)
        self.assertEqual(self.a.balance, 200)

        # lend 100 credit to A, relative fee is 0.1 * 100 = 10
        self.cf_price_rate.lend_credit(self.a, 100)
        self.assertEqual(self.cf_price_rate.get_total_credit(self.a), 100)
        self.assertEqual(self.cf_price_rate.get_total_fee(self.a), 10)
        self.assertEqual(self.a.balance, 300)

        # lend 100 credit to A, total fee is 25 (fixed fee = 15 and relative fee = 10)
        self.cf_price_combined.lend_credit(self.a, 100)
        self.assertEqual(self.cf_price_combined.get_total_credit(self.a), 100)
        self.assertEqual(self.cf_price_combined.get_total_fee(self.a), 25)
        self.assertEqual(self.a.balance, 400)

        
    def test_collect(self):
        # lend 100 credit to A with 15 fixed fee, after repayment, balance is 100 - 15 = 85 
        self.cf_price_fixed.lend_credit(self.a, 100)
        self.cf_price_fixed.collect_repayment(self.a)
        self.assertEqual(self.cf_price_fixed.get_total_credit(self.a), 0)
        self.assertEqual(self.cf_price_fixed.get_total_fee(self.a), 0)
        