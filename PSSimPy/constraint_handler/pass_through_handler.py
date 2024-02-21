from PSSimPy.constraint_handler.abstract_constraint_handler import AbstractConstraintHandler
from PSSimPy.transaction import Transaction

class PassThroughHandler(AbstractConstraintHandler):
    """No constraints"""

    def __init__(self):
        super().__init__()

    # implement abstract function
    def process_transaction(self, transaction: Transaction):        
        self.passed_transactions.append(transaction)