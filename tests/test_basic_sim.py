import os
import copy
import unittest
import pandas as pd

import PSSimPy
from PSSimPy.credit_facilities import SimplePriced, SimpleCollateralized
from PSSimPy.queues import PriorityQueue, FIFOQueue
from PSSimPy.simulator import BasicSim
from PSSimPy.utils import is_valid_24h_time


class TestBasicSimMultipleDays(unittest.TestCase):
    def setUp(self) -> None:
        self.sim_ids = ["Base", "EOD-1", "EOD-2"]
        
        self.output_log_paths = []
        self.output_log_paths.extend([f'{id}-processed_transactions.csv' for id in self.sim_ids])
        self.output_log_paths.extend([f'{id}-transaction_fees.csv' for id in self.sim_ids])
        self.output_log_paths.extend([f'{id}-queue_stats.csv' for id in self.sim_ids])
        self.output_log_paths.extend([f'{id}-account_balance.csv' for id in self.sim_ids])
        self.output_log_paths.extend([f'{id}-credit_facility.csv' for id in self.sim_ids])

        self.banks = {'name': ['b1', 'b2', 'b3'], 'bank_code': ['ABC', 'KLM', 'XYZ']}

        self.accounts = pd.DataFrame([
            {'id': 'acc1', 'owner': 'b1', 'balance': 50, 'posted_collateral': 0},
            {'id': 'acc2', 'owner': 'b2', 'balance': 50, 'posted_collateral': 0},
            {'id': 'acc3', 'owner': 'b3', 'balance': 50, 'posted_collateral': 0},
        ])

        self.transactions = pd.DataFrame([
            {'sender_account': 'acc1', 'recipient_account': 'acc2', 'amount': 100, 'day':1, 'time': '08:30'},
            {'sender_account': 'acc2', 'recipient_account': 'acc3', 'amount': 100, 'day':1, 'time': '09:00'},
            {'sender_account': 'acc3', 'recipient_account': 'acc1', 'amount': 100, 'day':1, 'time': '09:30'},
            {'sender_account': 'acc1', 'recipient_account': 'acc2', 'amount': 200, 'day':2, 'time': '08:30'},
            {'sender_account': 'acc2', 'recipient_account': 'acc3', 'amount': 200, 'day':2, 'time': '09:00'},
            {'sender_account': 'acc3', 'recipient_account': 'acc1', 'amount': 200, 'day':2, 'time': '09:30'},
            {'sender_account': 'acc1', 'recipient_account': 'acc2', 'amount': 300, 'day':3, 'time': '08:30'},
            {'sender_account': 'acc2', 'recipient_account': 'acc3', 'amount': 300, 'day':3, 'time': '09:00'},
            {'sender_account': 'acc3', 'recipient_account': 'acc1', 'amount': 300, 'day':3, 'time': '09:30'},
        ])

    def setup_params(self, queue, credit_facility, eod_clear_queue = False, eod_force_settlement = False):
        params = {
            "open_time": '08:00',
            "close_time": '10:00',
            "num_days": 3,
            "banks": copy.deepcopy(self.banks),
            "accounts": (self.accounts).copy(),
            "transactions": (self.transactions).copy(),
            "queue": queue,
            "credit_facility": credit_facility,
            "eod_clear_queue": eod_clear_queue,
            "eod_force_settlement": eod_force_settlement,
        }
        return params
        
    def tearDown(self):
        for path in self.output_log_paths:
            if os.path.exists(path): os.remove(path)

    def test_run_fifo_queue(self):
        # setup parameters for sim with NO EOD
        params = self.setup_params(FIFOQueue(), SimpleCollateralized())
        self.sim_base = BasicSim(self.sim_ids[0], **params)

        # setup parameters for sim with CLEAR QUEUE EOD
        params = self.setup_params(FIFOQueue(), SimpleCollateralized(), True, False)
        self.sim_setting_1 = BasicSim(self.sim_ids[1], **params)

        # setup parameters for sim with FORCE SETTLEMENT EOD
        params = self.setup_params(FIFOQueue(), SimpleCollateralized(), True, True)
        self.sim_setting_2 = BasicSim(self.sim_ids[2], **params)

        # run all simulation settings
        self.sim_base.run()
        self.sim_setting_1.run()
        self.sim_setting_2.run()

        # assert the number of queue at the end of simulation
        self.assertEqual(len(self.sim_base.queue.queue), 9)
        self.assertEqual(len(self.sim_setting_1.queue.queue), 0)
        self.assertEqual(len(self.sim_setting_2.queue.queue), 0)

        # assert transaction status code (0 for not settled/queued, -1 for rejected, 2 for settled)
        self.assertEqual(sum([trx[0].status_code for trx in self.sim_base.transactions]), 0)
        self.assertEqual(sum([trx[0].status_code for trx in self.sim_setting_1.transactions]), -9)
        self.assertEqual(sum([trx[0].status_code for trx in self.sim_setting_2.transactions]), 18)

    def test_run_priority_queue(self):
        for path in self.output_log_paths:
            if os.path.exists(path):
                os.remove(path)

        # setup parameters for sim with NO EOD
        params = self.setup_params(PriorityQueue(), SimpleCollateralized())
        self.sim_base = BasicSim(self.sim_ids[0], **params)

        # setup parameters for sim with CLEAR QUEUE EOD
        params = self.setup_params(PriorityQueue(), SimpleCollateralized(), True, False)
        self.sim_setting_1 = BasicSim(self.sim_ids[1], **params)

        # setup parameters for sim with FORCE SETTLEMENT EOD
        params = self.setup_params(PriorityQueue(), SimpleCollateralized(), True, True)
        self.sim_setting_2 = BasicSim(self.sim_ids[2], **params)

        # run all simulation settings
        self.sim_base.run()
        self.sim_setting_1.run()
        self.sim_setting_2.run()

        # assert the number of queue at the end of simulation
        self.assertEqual(len(self.sim_base.queue.queue), 9)
        self.assertEqual(len(self.sim_setting_1.queue.queue), 0)
        self.assertEqual(len(self.sim_setting_2.queue.queue), 0)

        # assert transaction status code (0 for not settled/queued, -1 for rejected, 2 for settled)
        self.assertEqual(sum([trx[0].status_code for trx in self.sim_base.transactions]), 0)
        self.assertEqual(sum([trx[0].status_code for trx in self.sim_setting_1.transactions]), -9)
        self.assertEqual(sum([trx[0].status_code for trx in self.sim_setting_2.transactions]), 18)



class TestBasicSim(unittest.TestCase):
    def setUp(self) -> None:
        self.banks = {'name': ['b1', 'b2', 'b3'], 'bank_code': ['ABC', 'KLM', 'XYZ']}
        self.accounts = {'id': ['acc1', 'acc2', 'acc3'],
                         'owner': ['b1', 'b2', 'b3'],
                         'balance': [200, 750, 1000],
                         'posted_collateral': [150, 0, 0]}
        self.transactions = pd.DataFrame([
            {'sender_account': 'acc1', 'recipient_account': 'acc2', 'amount': 250, 'day':1, 'time': '08:50'},
            {'sender_account': 'acc2', 'recipient_account': 'acc3', 'amount': 100, 'day':1, 'time': '09:00'},
            {'sender_account': 'acc1', 'recipient_account': 'acc3', 'amount': 110, 'day':1, 'time': '09:15'},
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
        all_transactions.sort(key=lambda x: x[2])
        
        for i, (trx, _, t) in enumerate(all_transactions):
            # check transaction properties
            self.assertIsInstance(trx, PSSimPy.Transaction)
            self.assertTrue(is_valid_24h_time(t))
            
            # check valid transaction account data
            self.assertIn(trx.sender_account, self.sim.accounts.values())
            self.assertIn(trx.recipient_account, self.sim.accounts.values())
            
            # check transaction data
            self.assertEqual(self.transactions['sender_account'][i], trx.sender_account.id)
            self.assertEqual(self.transactions['recipient_account'][i], trx.recipient_account.id)
            self.assertEqual(self.transactions['amount'][i], trx.amount)
            self.assertEqual(self.transactions['time'][i], trx.time)
        
    def test_run_simple_priced(self):
        # reset credit facility as it doesn't reset after simulation in other test cases
        self.sim.credit_facility = SimplePriced(base_fee=10, base_rate=1.5)
        self.sim.run()
        
        for trx, _, _ in self.sim.transactions: 
            self.assertNotEqual(trx.status_code, 0)
        
        # each account's balance after simulation
        self.assertEqual(self.sim.accounts['acc1'].balance, 200 + 50 - 250 + 110 - 110)
        self.assertEqual(self.sim.accounts['acc2'].balance, 750 + 250 - 100)
        self.assertEqual(self.sim.accounts['acc3'].balance, 1000 + 100 + 110)
        
        # used credit facility after simulation
        self.assertEqual(self.sim.credit_facility.used_credit['acc1'], [50.0, 110.0])
        self.assertEqual(self.sim.credit_facility.used_credit['acc2'], [])
        self.assertEqual(self.sim.credit_facility.used_credit['acc3'], [])

        # history of credit facility
        self.assertEqual(self.sim.credit_facility.history['acc1'], [(1, 50.+110., (50*1.5+10)+(110*1.5+10))])
        self.assertEqual(self.sim.credit_facility.history['acc2'], [(1, 0, 0)])
        self.assertEqual(self.sim.credit_facility.history['acc3'], [(1, 0, 0)])
        
    def test_run_simple_collateralized(self):
        # reset credit facility as it doesn't reset after simulation in other test cases
        self.sim.credit_facility = SimpleCollateralized()
        self.sim.run()
        
        for trx, _, _ in self.sim.transactions: 
            self.assertNotEqual(trx.status_code, 0)
        
        # each account's balance after simulation, acc1 has negative balance (no constraint handler for it)
        self.assertEqual(self.sim.accounts['acc1'].balance, 200 + 50 - 250 - 110)
        self.assertEqual(self.sim.accounts['acc2'].balance, 750 + 250 - 100)
        self.assertEqual(self.sim.accounts['acc3'].balance, 1000 + 100 + 110)
        
        # acc1 posted collateral, used 50 from 150
        self.assertEqual(self.sim.accounts['acc1'].posted_collateral, 100)

        # used credit facility after simulation
        self.assertEqual(self.sim.credit_facility.used_credit['acc1'], [50.0])
        self.assertEqual(self.sim.credit_facility.used_credit['acc2'], [])
        self.assertEqual(self.sim.credit_facility.used_credit['acc3'], [])

        # history of credit facility
        self.assertEqual(self.sim.credit_facility.history['acc1'], [(1, 50.0, 0)])
        self.assertEqual(self.sim.credit_facility.history['acc2'], [(1, 0, 0)])
        self.assertEqual(self.sim.credit_facility.history['acc3'], [(1, 0, 0)])
    
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

if __name__ == '__main__':
    unittest.main()