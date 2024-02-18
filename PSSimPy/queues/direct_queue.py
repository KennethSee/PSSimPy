from PSSimPy.queues.abstract_queue import AbstractQueue
from PSSimPy.transaction import Transaction

class DirectQueue(AbstractQueue):
    
    def __init__(self):
        super().__init__()

    @staticmethod
    def sorting_logic(queue_item: tuple[Transaction, int]) -> int:
        _, period = queue_item
        return period
        
    @staticmethod
    def dequeue_criteria(queue_item: tuple[Transaction, int]) -> bool:
        return True