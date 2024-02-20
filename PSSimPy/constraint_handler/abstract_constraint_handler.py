from abc import ABC, abstractmethod
from PSSimPy import Transaction

class AbstractConstraintHandler(ABC):

    def __init__(self):
        # for key, value in kwargs.items():
        #     setattr(self, key, value)
        self.processed_transactions = {'pass': [], 'fail': []}
    
    @abstractmethod
    def process_transaction(self, transaction: Transaction) -> dict:
        """
        Should return a dictionary that consists of 'pass' and 'fail' as keys, 
        with the corresponding passed and failed transactions as values in the form of a list respectively.
        """
        pass