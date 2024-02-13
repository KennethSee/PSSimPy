from PSSimPy.transaction import Transaction
from abc import ABC, abstractmethod

class AbstractQueue(ABC):

    @abstractmethod
    def load_txn(self, transactions: list[Transaction]) -> None:
        pass
    
    @abstractmethod
    def enqueue(self, transaction: Transaction) -> None:
        pass
    
    @abstractmethod
    def dequeue(self) -> Transaction:
        pass
    
    @abstractmethod
    def sort(self) -> None:
        pass
    