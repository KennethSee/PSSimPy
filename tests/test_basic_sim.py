import os
import unittest
import pandas as pd

import PSSimPy
from PSSimPy.credit_facilities import SimplePriced
from PSSimPy.simulator import BasicSim
from PSSimPy.utils import is_valid_24h_time
from PSSimPy.constraint_handler import MinBalanceConstraintHandler

class TestBasicSim(unittest.TestCase):
    def setUp(self) -> None:
        self.banks = {'name': ['b1', 'b2', 'b3'], 'bank_code': ['ABC', 'KLM', 'XYZ']}
        self.accounts = {'id': ['acc1', 'acc2', 'acc3'], 'owner': ['b1', 'b2', 'b3'], 'balance': [200, 750, 1000]}
        self.transactions = pd.DataFrame([
            {'sender_account': 'acc1', 'receipient_account': 'acc2', 'amount': 250, 'time': '08:50'},
            {'sender_account': 'acc2', 'receipient_account': 'acc3', 'amount': 100, 'time': '09:00'},
            {'sender_account': 'acc1', 'receipient_account': 'acc3', 'amount': 110, 'time': '09:15'},
        ])
        self.sim = BasicSim('sim',
                            banks = self.banks, # dict input
                            accounts = self.accounts, # dict input
                            transactions = self.transactions, # pd.DataFrame input
                            open_time='08:00',
                            close_time='12:00',
                            num_days=1)
        self.output_log_path = 'sim-processed_transactions.csv'
        
    def tearDown(self):
        if os.path.exists(self.output_log_path):
            os.remove(self.output_log_path)
        
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

    def test_logger(self):
        self.sim.run()
        self.assertTrue(os.path.exists(self.output_log_path))
        df = pd.read_csv(self.output_log_path)
        self.assertEqual(df['time'].tolist(), ['08:45', '09:00', '09:15'])
        self.assertEqual(df['status'].tolist(), ['Success', 'Success', 'Success'])
        self.assertEqual(df['from_account'].tolist(), ['acc1', 'acc2', 'acc1'])
        self.assertEqual(df['to_account'].tolist(), ['acc2', 'acc3', 'acc3'])
        self.assertEqual(df['amount'].tolist(), [250, 100, 110])
        
    def test_run(self):
        # reset credit facility as it doesn't reset after simulation in other test cases
        self.sim.credit_facility = SimplePriced()
        self.sim.run()
        for trx, _ in self.sim.transactions: 
            self.assertNotEqual(trx.status_code, 0)
        
        # each account's balance after simulation
        self.assertEqual(self.sim.accounts['acc1'].balance, 200 + 50 - 250 + 110 - 110)
        self.assertEqual(self.sim.accounts['acc2'].balance, 750 + 250 - 100)
        self.assertEqual(self.sim.accounts['acc3'].balance, 1000 + 100 + 110)
        
        # used credit facility after simulation
        self.assertEqual(self.sim.credit_facility.used_credit['acc1'], [50.0, 110.0])
        self.assertEqual(self.sim.credit_facility.used_credit['acc2'], [])
        self.assertEqual(self.sim.credit_facility.used_credit['acc3'], [])