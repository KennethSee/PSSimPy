from PSSimPy.queues.abstract_queue import AbstractQueue
from PSSimPy.transaction import Transaction
from PSSimPy.utils import min_balance_maintained

class FIFOQueue(AbstractQueue):
    """This queue attempts to dequeue transactions that came in earlier first."""
    
    def __init__(self):
        super().__init__()

    @staticmethod
    def sorting_logic(queue_item: tuple[Transaction, int]) -> int:
        _, period = queue_item
        return period
        
    @staticmethod
    def dequeue_criteria(queue_item: tuple[Transaction, int]) -> bool:
        transaction, _ = queue_item
        return min_balance_maintained(transaction.sender_account, transaction.amount, min_balance=0)
