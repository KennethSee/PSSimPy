from abc import ABC, abstractmethod
from PSSimPy.transaction import Transaction

class AbstractConstraintHandler(ABC):

    def __init__(self):
        self.passed_transactions = []
    
    @abstractmethod
    def process_transaction(self, transaction: Transaction):
        """Should return a list of passed transactions to be sent for further processing."""
        pass

    def get_passed_transactions(self):
        """Returns the list of passed transactions."""
        return self.passed_transactions
    
    def clear(self):
        self.passed_transactions = []