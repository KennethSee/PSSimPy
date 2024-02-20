from PSSimPy.constraint_handler import AbstractSettlementMechanism
from PSSimPy import Transaction

class SimpleConstraintHandler(AbstractConstraintHandler):
    """Splits a transaction if it exceeds max size"""

    def __init__(self, max_txn_size: float):
        super().__init__()
        self.max_txn_size = max_txn_size

    def process_transaction(self, transaction: Transaction) -> dict:
        sender = transaction.sender_account
        receipient = transaction.receipient_account
        # check if transaction size exceeds max size
        if transaction.amount > self.max_txn_size:
            # split transactions
            tx1 = Transaction(
                sender_account = transaction.sender_account,
                receipient_account = transaction.receipient_account,
                amount = self.max_txn_size,
                priority = transaction.priority,
                transaction.kwargs
                )
            tx2 = Transaction(
                sender_account = transaction.sender_account,
                receipient_account = transaction.receipient_account,
                amount = transaction.amount - self.max_txn_size,
                priority = transaction.priority,
                transaction.kwargs
                )
            # to-do: reprocess split transactions

        else:
            self.processed_transactions['pass'].append(transaction)

        return self.processed_transactions