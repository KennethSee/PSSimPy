import os
import unittest
import pandas as pd

import PSSimPy
from PSSimPy.credit_facilities import SimplePriced
from PSSimPy.simulator import BasicSim
from PSSimPy.utils import is_valid_24h_time

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
        self.output_log_paths = {
            'transactions': 'sim-processed_transactions.csv',
            'fees': 'sim-transaction_fees.csv',
            'queues': 'sim-queue_stats.csv',
            'accounts': 'sim-account_balance.csv',
            'credits': 'sim-credit_facility.csv',
        }
        
    def tearDown(self):
        for path in self.output_log_paths.values():
            if os.path.exists(path): os.remove(path)
        
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
    
    def test_logger(self):
        self.tearDown()

        # reset credit facility as it doesn't reset after simulation in other test cases
        self.sim.credit_facility = SimplePriced()
        self.sim.run()
        
        for path in self.output_log_paths.values():
            self.assertTrue(os.path.exists(path))
        
        txn = pd.read_csv(self.output_log_paths['transactions'])
        self.assertEqual(txn['time'].tolist(), ['08:45', '09:00', '09:15'])
        self.assertEqual(txn['status'].tolist(), ['Success', 'Success', 'Success'])
        self.assertEqual(txn['from_account'].tolist(), ['acc1', 'acc2', 'acc1'])
        self.assertEqual(txn['to_account'].tolist(), ['acc2', 'acc3', 'acc3'])
        self.assertEqual(txn['amount'].tolist(), [250, 100, 110])
        
        crdt = pd.read_csv(self.output_log_paths['credits'])
        self.assertEqual(crdt[(crdt['account'] == 'acc1') & (crdt['time'] == '08:00')]['total_credit'].values[0], 0.)
        self.assertEqual(crdt[(crdt['account'] == 'acc1') & (crdt['time'] == '08:45')]['total_credit'].values[0], 50.)
        self.assertEqual(crdt[(crdt['account'] == 'acc1') & (crdt['time'] == '11:45')]['total_credit'].values[0], 160.)
        
        acc = pd.read_csv(self.output_log_paths['accounts'])
        self.assertListEqual(acc[acc['time'] == '08:00']['balance'].tolist(), [200.0, 750.0, 1000.0])
        self.assertListEqual(acc[acc['time'] == '11:45']['balance'].tolist(), [0.0, 900.0, 1210.0])