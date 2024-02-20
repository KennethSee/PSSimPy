import unittest

from PSSimPy.constraint_handler import MaxSizeConstraintHandler, MinBalanceConstraintHandler, PassThroughHandler
from PSSimPy import Transaction
from PSSimPy import Account
from PSSimPy.utils import TRANSACTION_STATUS_CODES


class TestConstraintHandler(unittest.TestCase):

    def setUp(self) -> None:
        self.acc1 = Account('acc1', None, 1000000000)
        self.acc2 = Account('acc2', None, 1000000000)
        self.acc3 = Account('acc3', None, 100)
        self.txn1 = Transaction(self.acc1, self.acc2, 100)
        self.txn2 = Transaction(self.acc1, self.acc2, 200)
        self.txn3 = Transaction(self.acc1, self.acc2, 205)
        self.txn4 = Transaction(self.acc3, self.acc1, 100)
        self.txn5 = Transaction(self.acc3, self.acc1, 101)
        self.pass_through_handler = PassThroughHandler()
        self.max_size_constraint_handler = MaxSizeConstraintHandler(max_txn_size=100)
        self.min_balance_constraint_handler = MinBalanceConstraintHandler(min_balance=0)

    def test_initialization(self):
        self.assertEqual(len(self.pass_through_handler.passed_transactions), 0, 'Passed transactions should be empty upon initialization')
        self.assertEqual(len(self.max_size_constraint_handler.passed_transactions), 0, 'Passed transactions should be empty upon initialization')

    def test_pass_through(self):
        for txn in [self.txn1, self.txn2, self.txn3, self.txn4, self.txn5]:
            self.pass_through_handler.process_transaction(txn)
        passed_transactions = self.pass_through_handler.get_passed_transactions()
        self.assertEqual(len(passed_transactions), 5)

    def test_process_transaction_regular(self):
        self.max_size_constraint_handler.process_transaction(self.txn1)
        self.assertEqual(len(self.max_size_constraint_handler.passed_transactions), 1, 'There should only be 1 transaction processed for txn1')
        self.assertEqual(self.max_size_constraint_handler.passed_transactions[0].amount, 100)

        self.min_balance_constraint_handler.process_transaction(self.txn4)
        self.assertEqual(len(self.min_balance_constraint_handler.passed_transactions), 1)

    def test_process_transaction_split(self):
        self.max_size_constraint_handler.process_transaction(self.txn2)
        self.assertEqual(len(self.max_size_constraint_handler.passed_transactions), 2, 'There should be 2 transactions processed for txn2')
        self.assertEqual(self.max_size_constraint_handler.passed_transactions[0].amount, 100)
        self.assertEqual(self.max_size_constraint_handler.passed_transactions[1].amount, 100)
        self.assertEqual(self.txn2.status_code, TRANSACTION_STATUS_CODES['Modified'], 'Original transaction should have modified trransaction status')
        self.assertEqual(self.max_size_constraint_handler.passed_transactions[1].status_code, TRANSACTION_STATUS_CODES['Open'])

        self.max_size_constraint_handler.process_transaction(self.txn3)
        self.assertEqual(len(self.max_size_constraint_handler.passed_transactions), 5, 'There should now be 5 transactions processed for txn2 and txn3')
        self.assertEqual(self.max_size_constraint_handler.passed_transactions[2].amount, 100)
        self.assertEqual(self.max_size_constraint_handler.passed_transactions[4].amount, 5)

    def test_process_transaction_fail(self):
        self.min_balance_constraint_handler.process_transaction(self.txn5)
        self.assertEqual(len(self.min_balance_constraint_handler.passed_transactions), 0)
        self.assertEqual(self.txn5.status_code, TRANSACTION_STATUS_CODES['Failed'])

if __name__ == '__main__':
    unittest.main()