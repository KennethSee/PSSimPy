import os
import copy
import unittest
import pandas as pd

import PSSimPy
from PSSimPy import Bank
from PSSimPy.credit_facilities import SimplePriced, SimpleCollateralized
from PSSimPy.queues import PriorityQueue, FIFOQueue
from PSSimPy.simulator import ABMSim
from PSSimPy.utils import is_valid_24h_time

class CautiousBank(Bank):
    """This bank will not settle transactions in the first period it arrives."""

    def __init__(self, name, strategy_type='Cautious', **kwargs):
        super().__init__(name, strategy_type, **kwargs)
    
    # overwrite strategy
    def strategy(self, txns_to_settle: set, all_outstanding_transactions: set, sim_name: str, day: int, current_time: str, queue) -> set:
        return {txn for txn in txns_to_settle if txn.time != current_time}
    

class TestTransactionSettleInfo(unittest.TestCase):

    def setUp(self):
        self.sim_ids = ["WithoutDelay", "WithDelay"]
        
        self.output_log_paths = []
        self.output_log_paths.extend([f'{id}-processed_transactions.csv' for id in self.sim_ids])
        self.output_log_paths.extend([f'{id}-transaction_fees.csv' for id in self.sim_ids])
        self.output_log_paths.extend([f'{id}-queue_stats.csv' for id in self.sim_ids])
        self.output_log_paths.extend([f'{id}-account_balance.csv' for id in self.sim_ids])
        self.output_log_paths.extend([f'{id}-credit_facility.csv' for id in self.sim_ids])

        self.banks = {'name': ['b1', 'b2'], 'bank_code': ['ABC', 'KLM']}
        self.accounts = pd.DataFrame([
            {'id': 'acc1', 'owner': 'b1', 'balance': 1000, 'posted_collateral': 0},
            {'id': 'acc2', 'owner': 'b2', 'balance': 1000, 'posted_collateral': 0},
        ])
        self.transactions = pd.DataFrame([
            {'sender_account': 'acc1', 'recipient_account': 'acc2', 'amount': 100, 'day':1, 'time': '08:00'}
        ])

    def tearDown(self):
        for path in self.output_log_paths:
            if os.path.exists(path): os.remove(path)

    def setup_params(self, banks, queue, credit_facility, eod_clear_queue = False, eod_force_settlement = False):
        params = {
            "open_time": '08:00',
            "close_time": '10:00',
            "num_days": 3,
            "banks": copy.deepcopy(banks),
            "accounts": (self.accounts).copy(),
            "transactions": (self.transactions).copy(),
            "queue": queue,
            "credit_facility": credit_facility,
            "eod_clear_queue": eod_clear_queue,
            "eod_force_settlement": eod_force_settlement,
            "strategy_mapping": {"Cautious": CautiousBank, "Standard": Bank}
        }
        return params

    def test_no_delay(self):
        banks = copy.deepcopy(self.banks)
        banks['strategy_type'] = ['Standard', 'Standard']
        params = self.setup_params(banks, FIFOQueue(), SimpleCollateralized())
        sim = ABMSim(self.sim_ids[0], **params)

        sim.run()
        for txn, _, _ in sim.transactions:
            self.assertEqual(txn.time, txn.settle_time)
            self.assertEqual(txn.day, txn.settle_day)

    def test_with_delay(self):
        banks = copy.deepcopy(self.banks)
        banks['strategy_type'] = ['Cautious', 'Cautious']
        params = self.setup_params(banks, FIFOQueue(), SimpleCollateralized())
        sim = ABMSim(self.sim_ids[1], **params)

        sim.run()
        for txn, _, _ in sim.transactions:
            self.assertNotEqual(txn.time, txn.settle_time)
            self.assertEqual(txn.day, txn.settle_day)
            self.assertEqual('08:15', txn.settle_time)


if __name__ == '__main__':
    unittest.main()