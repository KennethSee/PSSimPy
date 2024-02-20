import unittest

from PSSimPy.constraint_handler import AbstractConstraintHandler, MaxSizeConstraintHandler, MinBalanceConstraintHandler, PassThroughHandler
from PSSimPy import Transaction
from PSSimPy import Account


class TestConstraintHandler(unittest.TestCase):

    def setUp(self) -> None:
        self.acc1 = Account('acc1', None, 1000000000)
        self.acc2 = Account('acc2', None, 1000000000)
        self.acc3 = Account('acc3', None, 1000000000)
        self.txn1 = Transaction(self.acc1, self.acc2, 100)
        self.txn2 = Transaction(self.acc1, self.acc2, 200)
        self.txn3 = Transaction(self.acc1, self.acc2, 205)
        self.simple_constraint_handler = MaxSizeConstraintHandler(max_txn_size=100)

    def test_initialization(self):
        self.assertEqual(len(self.simple_constraint_handler.passed_transactions), 0, 'Passed transactions should be empty upon initialization')

    def test_process_transaction_regular(self):
        self.simple_constraint_handler.process_transaction(self.txn1)
        self.assertEqual(len(self.simple_constraint_handler.passed_transactions), 1, 'There should only be 1 transaction processed for txn1')
        self.assertEqual(self.simple_constraint_handler.passed_transactions[0].amount, 100)

    def test_process_transaction_split(self):
        self.simple_constraint_handler.process_transaction(self.txn2)
        self.assertEqual(len(self.simple_constraint_handler.passed_transactions), 2, 'There should be 2 transactions processed for txn2')
        self.assertEqual(self.simple_constraint_handler.passed_transactions[0].amount, 100)
        self.assertEqual(self.simple_constraint_handler.passed_transactions[1].amount, 100)

        self.simple_constraint_handler.process_transaction(self.txn3)
        self.assertEqual(len(self.simple_constraint_handler.passed_transactions), 5, 'There should now be 5 transactions processed for txn2 and txn3')
        self.assertEqual(self.simple_constraint_handler.passed_transactions[2].amount, 100)
        self.assertEqual(self.simple_constraint_handler.passed_transactions[4].amount, 5)

if __name__ == '__main__':
    unittest.main()