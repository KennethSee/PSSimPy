from typing import Tuple
from PSSimPy.transaction import Transaction
from abc import ABC, abstractmethod
from sortedcontainers import SortedList

class AbstractQueue(ABC):

    def __init__(self):
        self.period_counter = 0 # to track when 
        self.queue = SortedList(key=self.sorting_logic)

    def next_period(self):
        self.period_counter += 1

    def reset_period(self):
        self.period_counter = 0

    @staticmethod
    @abstractmethod
    def sorting_logic(queue_item: Tuple[Transaction, int]) -> int:
        """
        This sets the logic for how the queue is ordered.
        It should be implemented such that for a given tuple with the transaction and the period when it entered the queue, a postive integer is returned which represents its priority in the queue.
        The smaller the integer, the higher the priority.
        """
        pass

    @staticmethod
    @abstractmethod
    def dequeue_criteria(queue_item: tuple[Transaction, int]) -> bool:
        """
        This sets the criteria for whether a transaction is eligible to be dequeued.
        If the transaction passes the checks, it should return true.
        """
        pass
    
    def enqueue(self, transaction: Transaction) -> None:
        self.queue.add((transaction, self.period_counter))

    def bulk_enqueue(self, transactions: set[Transaction]) -> None:
        for transaction in transactions:
            self.enqueue(transaction)
    
    def dequeue(self, queue_item: tuple[Transaction, int]) -> Transaction:
        self.queue.remove(queue_item)

    def begin_dequeueing(self) -> list[Transaction]:
        items_to_dequeue = []
        for item in self.queue:
            if self.dequeue_criteria(item):
                items_to_dequeue.append(item)
        for item in items_to_dequeue:
            self.dequeue(item)
        return [transaction for transaction, _ in items_to_dequeue]
    
    def get_num_txns(self) -> int:
        return len(self.queue)

    def get_txn_amount_total(self) -> float:
        total_amount = sum([transaction.amount for transaction, _ in self.queue])
        return total_amount

