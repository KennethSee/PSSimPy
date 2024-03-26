import unittest
from unittest.mock import patch
from PSSimPy import Account, Transaction
from PSSimPy.utils import TRANSACTION_STATUS_CODES

class TestTransaction(unittest.TestCase):

    def setUp(self):
        self.acc1 = Account('acc1', None, 1000000000)
        self.acc2 = Account('acc2', None, 1000000000)
        self.acc3 = Account('acc3', None, 100)
        self.txn1 = Transaction(self.acc1, self.acc2, 100)
        self.txn2 = Transaction(self.acc1, self.acc2, 200, 2)
        self.txn3 = Transaction(self.acc1, self.acc2, 205)
        self.txn4 = Transaction(self.acc3, self.acc1, 100)
        self.txn5 = Transaction(self.acc3, self.acc1, 101)

    def test_initialization(self):
        self.assertEqual(self.txn1.sender_account, self.acc1)
        self.assertEqual(self.txn1.recipient_account, self.acc2)
        self.assertEqual(self.txn1.amount, 100)
        self.assertEqual(self.txn1.priority, 1)
        self.assertEqual(self.txn2.priority, 2)

    @patch('builtins.print')
    def test_update_transaction_status(self, mock_print):
        self.assertEqual(self.txn1.status_code, TRANSACTION_STATUS_CODES['Open'])
        self.txn1.update_transaction_status('Failed')
        self.assertEqual(self.txn1.status_code, TRANSACTION_STATUS_CODES['Failed'])
        # test KeyError handling
        self.txn1.update_transaction_status('Not a valid status')
        mock_print.assert_called_once_with("Invalid status: 'Not a valid status'. Please provide a valid transaction status.")

    def test_get_instance(self):
        self.assertEqual(len(Transaction.get_instances()), 5)
        new_txn = Transaction(self.acc3, self.acc2, 1)
        self.assertEqual(len(Transaction.get_instances()), 6)

    def test_clear_instance(self):
        Transaction.clear_instances()
        self.assertEqual(len(Transaction.get_instances()), 0)


if __name__ == '__main__':
    unittest.main()