from PSSimPy.constraint_handler.abstract_constraint_handler import AbstractConstraintHandler
from PSSimPy.transaction import Transaction

class MaxSizeConstraintHandler(AbstractConstraintHandler):
    """Splits a transaction if it exceeds max size"""

    def __init__(self, max_txn_size: float):
        super().__init__()
        self.max_txn_size = max_txn_size

    # implement abstract function
    def process_transaction(self, transaction: Transaction):
        """Process a transaction, splitting it if it exceeds max size and ensuring all resulting transactions pass."""
        kwargs = (transaction.kwargs if hasattr(transaction, 'kwargs') else {})

        # Check if transaction size exceeds max size
        if transaction.amount > self.max_txn_size:
            # Split the transaction
            txn1 = Transaction(
                sender_account=transaction.sender_account,
                receipient_account=transaction.receipient_account,
                amount=self.max_txn_size,
                priority=transaction.priority,
                **kwargs
            )
            txn2 = Transaction(
                sender_account=transaction.sender_account,
                receipient_account=transaction.receipient_account,
                amount=transaction.amount - self.max_txn_size,
                priority=transaction.priority,
                **kwargs
            )

            # Update original transaction to update status
            transaction.update_transaction_status('Modified')

            # Recursively process the split transactions
            self.process_transaction(txn1)
            self.process_transaction(txn2)
        else:
            # If transaction does not exceed max size, consider it passed
            self.passed_transactions.append(transaction)