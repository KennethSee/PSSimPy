from PSSimPy.queues.abstract_queue import AbstractQueue
from PSSimPy.transaction import Transaction

class DirectQueue(AbstractQueue):
    
    def __init__(self, transactions: list[Transaction] = None) -> None:
        super().__init__()
        self.queue = []
        
        if transactions is not None:
            self.load_txn(transactions)
        
    def enqueue(self, transaction: Transaction) -> None:
        self.queue.append(transaction)
        
    def dequeue(self) -> Transaction:
        return self.queue.pop()
    
    def load_txn(self, transactions: list[Transaction]) -> None:
        self.queue.extend(transactions)
    
    def sort(self) -> None:
        pass