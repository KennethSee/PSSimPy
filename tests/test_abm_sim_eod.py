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

class PettyBank(Bank):
    """This class of banks will not settle transactions to another bank's account if the counter party has an outstanding transaction to this bank that is not yet settled."""

    def __init__(self, name, strategy_type='Petty', **kwargs):
        super().__init__(name, strategy_type, **kwargs)
    
    # overwrite strategy
    def strategy(self, txns_to_settle: set, all_outstanding_transactions: set, sim_name: str, day: int, current_time: str, queue) -> set:
        # identify the counterparty bank of outstanding transactions where this bank is the recipient bank
        counterparties_with_outstanding = {transaction.sender_account.owner.name for transaction in all_outstanding_transactions if transaction.recipient_account.owner.name == self.name}
        # exclude transactions which involve paying the identified counterparties
        chosen_txns_to_settle = {transaction for transaction in txns_to_settle if transaction.recipient_account.owner.name not in counterparties_with_outstanding}
        return chosen_txns_to_settle

class TestABMSimEOD(unittest.TestCase):

    def setUp(self):
        self.sim_ids = ["Base", "ForceSettlement", "CarryForwardOutstanding"]
        
        self.output_log_paths = []
        self.output_log_paths.extend([f'{id}-processed_transactions.csv' for id in self.sim_ids])
        self.output_log_paths.extend([f'{id}-transaction_fees.csv' for id in self.sim_ids])
        self.output_log_paths.extend([f'{id}-queue_stats.csv' for id in self.sim_ids])
        self.output_log_paths.extend([f'{id}-account_balance.csv' for id in self.sim_ids])
        self.output_log_paths.extend([f'{id}-credit_facility.csv' for id in self.sim_ids])


        self.banks = {'name': ['b1', 'b2', 'b3'], 'bank_code': ['ABC', 'KLM', 'XYZ']}

        self.accounts = pd.DataFrame([
            {'id': 'acc1', 'owner': 'b1', 'balance': 1000, 'posted_collateral': 0},
            {'id': 'acc2', 'owner': 'b2', 'balance': 1000, 'posted_collateral': 0},
            {'id': 'acc3', 'owner': 'b3', 'balance': 1000, 'posted_collateral': 0},
        ])

        self.transactions = pd.DataFrame([
            {'sender_account': 'acc1', 'recipient_account': 'acc2', 'amount': 100, 'day':1, 'time': '08:30'},
            {'sender_account': 'acc2', 'recipient_account': 'acc3', 'amount': 100, 'day':1, 'time': '09:00'},
            {'sender_account': 'acc3', 'recipient_account': 'acc1', 'amount': 100, 'day':1, 'time': '09:30'},
            {'sender_account': 'acc1', 'recipient_account': 'acc2', 'amount': 200, 'day':2, 'time': '08:30'},
            {'sender_account': 'acc2', 'recipient_account': 'acc3', 'amount': 200, 'day':2, 'time': '09:00'},
            {'sender_account': 'acc3', 'recipient_account': 'acc2', 'amount': 200, 'day':2, 'time': '09:00'},
            {'sender_account': 'acc3', 'recipient_account': 'acc1', 'amount': 200, 'day':2, 'time': '09:30'},
            {'sender_account': 'acc1', 'recipient_account': 'acc2', 'amount': 300, 'day':3, 'time': '08:30'},
            {'sender_account': 'acc2', 'recipient_account': 'acc3', 'amount': 300, 'day':3, 'time': '09:00'},
            {'sender_account': 'acc3', 'recipient_account': 'acc1', 'amount': 300, 'day':3, 'time': '09:30'},
        ])

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
            "strategy_mapping": {"Petty": PettyBank, "Standard": Bank}
        }
        return params
    
    def tearDown(self):
        for path in self.output_log_paths:
            if os.path.exists(path): os.remove(path)
    
    def test_base(self):
        banks = copy.deepcopy(self.banks)
        banks['strategy_type'] = ['Standard', 'Standard', 'Standard']
        params = self.setup_params(banks, FIFOQueue(), SimpleCollateralized())
        sim_base = ABMSim(self.sim_ids[0], **params)

        sim_base.run()

        # assert the number of queue at the end of simulation
        self.assertEqual(len(sim_base.queue.queue), 0)

        # assert transaction status code (0 for not settled/queued, -1 for rejected, 2 for settled)
        self.assertEqual(sum([trx[0].status_code for trx in sim_base.transactions]), 10*2)

    def test_force_settlement(self):
        banks = copy.deepcopy(self.banks)
        banks['strategy_type'] = ['Standard', 'Petty', 'Petty']
        params = self.setup_params(banks, FIFOQueue(), SimpleCollateralized(), eod_force_settlement=True)
        sim_force_settlement = ABMSim(self.sim_ids[1], **params)

        sim_force_settlement.run()

        # assert transaction status code (0 for not settled/queued, -1 for rejected, 2 for settled)
        self.assertEqual(sum([trx[0].status_code for trx in sim_force_settlement.transactions]), 10*2)

    def test_carry_forward_outstanding(self):
        banks = copy.deepcopy(self.banks)
        banks['strategy_type'] = ['Standard', 'Petty', 'Petty']
        params = self.setup_params(banks, FIFOQueue(), SimpleCollateralized())
        sim_carry_forward = ABMSim(self.sim_ids[1], **params)

        sim_carry_forward.run()

        # assert transaction status code (0 for not settled/queued, -1 for rejected, 2 for settled)
        self.assertEqual(sum([trx[0].status_code for trx in sim_carry_forward.transactions]), 7*2)

if __name__ == '__main__':
    unittest.main()