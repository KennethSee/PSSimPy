from PSSimPy.constraint_handler.abstract_constraint_handler import AbstractConstraintHandler
from PSSimPy.transaction import Transaction
from PSSimPy.utils.account_utils import min_balance_maintained

class MinBalanceConstraintHandler(AbstractConstraintHandler):
    """
    This sets a minimum balance within the sender's account as a hard constraint for the transaction to be processed.
    Transactions that violate this constraint will be failed.
    """

    def __init__(self, min_balance: int=0):
        super().__init__()
        self.min_balance = min_balance

    # implement abstract function
    def process_transaction(self, transaction: Transaction):
        if min_balance_maintained(transaction.sender_account, transaction.amount, self.min_balance):
            self.passed_transactions.append(transaction)
        else:
            transaction.update_transaction_status('Failed')