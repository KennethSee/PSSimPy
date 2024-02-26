from PSSimPy import Transaction, Account
from PSSimPy.utils import TRANSACTION_LOGGER_HEADER, Logger
from PSSimPy.simulator import ABMSim

acc1 = Account('acc1', None, 1000000000)
acc2 = Account('acc2', None, 1000000000)
acc3 = Account('acc3', None, 100)
txn1 = Transaction(acc1, acc2, 100, 1)
txn2 = Transaction(acc1, acc2, 200, 2)
txn3 = Transaction(acc1, acc2, 205, 1)
txn4 = Transaction(acc3, acc1, 100, 3)
txn5 = Transaction(acc3, acc1, 101, 1)

txn1.update_transaction_status('Success')
txn2.update_transaction_status('Success')
txn3.update_transaction_status('Failed')
txn4.update_transaction_status('Success')
txn5.update_transaction_status('Success')

transaction_logger = Logger('processed_transactions', TRANSACTION_LOGGER_HEADER)
transactions = ABMSim._extract_logging_details({txn1, txn2, txn3, txn4, txn5}, 1, '08:15')
transaction_logger.write(transactions)