import unittest
import pandas as pd

import PSSimPy
from PSSimPy.simulator import BasicSim
from PSSimPy.utils import is_valid_24h_time

class TestBasicSim(unittest.TestCase):
    def setUp(self) -> None:
        self.banks = {'name': ['b1', 'b2', 'b3'], 'bank_code': ['ABC', 'KLM', 'XYZ']}
        self.accounts = {'id': ['acc1', 'acc2', 'acc3'], 'owner': ['b1', 'b2', 'b3'], 'balance': [500, 750, 1000]}
        self.transactions = pd.DataFrame([
            {'sender_account': 'acc1', 'receipient_account': 'acc2', 'amount': 100, 'time': '08:50'},
            {'sender_account': 'acc1', 'receipient_account': 'acc3', 'amount':  75, 'time': '09:00'},
            {'sender_account': 'acc2', 'receipient_account': 'acc3', 'amount': 150, 'time': '09:10'},
        ])
        self.sim = BasicSim('sim',
                            banks = self.banks,
                            accounts = self.accounts,
                            transactions = self.transactions,
                            open_time='08:00',
                            close_time='12:00')

    def test_bank_instances(self):
        for i, (bank_name, bank_obj) in enumerate(self.sim.banks.items()):
            # check bank instance
            self.assertIsInstance(bank_obj, PSSimPy.Bank)
            self.assertEqual(bank_name, bank_obj.name)
            
            # check bank data
            self.assertEqual(self.banks['name'][i], bank_obj.name)
            self.assertEqual(self.banks['bank_code'][i], bank_obj.bank_code)
            
    def test_account_instances(self):
        for i, (acc_id, acc_obj) in enumerate(self.sim.accounts.items()):
            # check account instance
            self.assertIsInstance(acc_obj, PSSimPy.Account)
            self.assertEqual(acc_id, acc_obj.id)

            # check account data
            self.assertEqual(self.accounts['id'][i], acc_obj.id)
            self.assertEqual(self.accounts['owner'][i], acc_obj.owner.name)
            self.assertEqual(self.accounts['balance'][i], acc_obj.balance)
    
    def test_transaction_instances(self): 
        # convert set into list and sort based on time      
        all_transactions = list(self.sim.transactions)
        all_transactions.sort(key=lambda x: x[1])
        
        for i, (trx, t) in enumerate(all_transactions):
            # check transaction properties
            self.assertIsInstance(trx, PSSimPy.Transaction)
            self.assertTrue(is_valid_24h_time(t))
            
            # check valid transaction account data
            self.assertIn(trx.sender_account, self.sim.accounts.values())
            self.assertIn(trx.receipient_account, self.sim.accounts.values())
            
            # check transaction data
            self.assertEqual(self.transactions['sender_account'][i], trx.sender_account.id)
            self.assertEqual(self.transactions['receipient_account'][i], trx.receipient_account.id)
            self.assertEqual(self.transactions['amount'][i], trx.amount)
            self.assertEqual(self.transactions['time'][i], trx.time)
