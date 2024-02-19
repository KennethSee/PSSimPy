from PSSimPy.queues.abstract_queue import AbstractQueue
from PSSimPy.transaction import Transaction
from PSSimPy.utils import min_balance_maintained

class PriorityQueue(AbstractQueue):
    """This queue dequeues transactions based on the order of their priorities."""
    
    def __init__(self):
        super().__init__()

    @staticmethod
    def sorting_logic(queue_item: tuple[Transaction, int]) -> int:
        transaction, _ = queue_item
        priority = transaction.priority
        return priority
        
    @staticmethod
    def dequeue_criteria(queue_item: tuple[Transaction, int]) -> bool:
        transaction, _ = queue_item
        return min_balance_maintained(transaction.sender_account, transaction.amount, min_balance=0)
