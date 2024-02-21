import unittest

from PSSimPy.constraint_handler import MaxSizeConstraintHandler, MinBalanceConstraintHandler, PassThroughHandler
from PSSimPy.queues import DirectQueue, PriorityQueue, FIFOQueue
from PSSimPy import Transaction, Account, System
from PSSimPy.utils import TRANSACTION_STATUS_CODES


class TestSystem(unittest.TestCase):

    def setUp(self) -> None:
        self.acc1 = Account('acc1', None, 1000000000)
        self.acc2 = Account('acc2', None, 1000000000)
        self.acc3 = Account('acc3', None, 100)
        self.txn1 = Transaction(self.acc1, self.acc2, 100, 1)
        self.txn2 = Transaction(self.acc1, self.acc2, 200, 2)
        self.txn3 = Transaction(self.acc1, self.acc2, 205, 1)
        self.txn4 = Transaction(self.acc3, self.acc1, 100, 3)
        self.txn5 = Transaction(self.acc3, self.acc1, 101, 1)
        self.pass_through_handler = PassThroughHandler()
        self.max_size_constraint_handler = MaxSizeConstraintHandler(max_txn_size=100)
        self.min_balance_constraint_handler = MinBalanceConstraintHandler(min_balance=0)
        self.direct_queue = DirectQueue()
        self.priority_queue = PriorityQueue()
        self.fifo_queue = FIFOQueue()

    def test_process_success(self):
        system = System(self.pass_through_handler, self.direct_queue)
        txns_to_process = set([self.txn1, self.txn2, self.txn3])
        system.process(txns_to_process)
        # check if transaction status is updated
        for txn in txns_to_process:
            self.assertEqual(txn.status_code, TRANSACTION_STATUS_CODES['Success'], 'Processed transactions should have status reflected as "Successful"')
        # check account balances are updated
        self.assertEqual(self.acc1.balance, 1000000000 - 505)
        self.assertEqual(self.acc2.balance, 1000000000 + 505)

    def test_repeat_process(self):
        """Check that transactions from a previous batch do not leak into new batch"""
        system = System(self.pass_through_handler, self.direct_queue)
        txns_to_process = set([self.txn1, self.txn2, self.txn3])
        processed_txns = system.process(txns_to_process)
        self.assertEqual(len(processed_txns), 3)

        new_txns_to_process = set([self.txn4, self.txn5])
        processed_txns = system.process(new_txns_to_process) # need to fix
        self.assertEqual(len(processed_txns), 2)

    def test_process_split(self):
        system = System(self.max_size_constraint_handler, self.direct_queue)
        txns_to_process = set([self.txn1, self.txn2, self.txn3])
        self.assertEqual(len(Transaction.get_instances()), 5)
        system.process(txns_to_process)
        self.assertEqual(len(Transaction.get_instances()), 11)

        # check status
        self.assertEqual(self.txn1.status_code, TRANSACTION_STATUS_CODES['Success'])
        self.assertEqual(self.txn2.status_code, TRANSACTION_STATUS_CODES['Modified'])
        self.assertEqual(self.txn3.status_code, TRANSACTION_STATUS_CODES['Modified'])


if __name__ == '__main__':
    unittest.main()