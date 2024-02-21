from PSSimPy.transaction import Transaction
from PSSimPy.constraint_handler.abstract_constraint_handler import AbstractConstraintHandler
from PSSimPy.queues.abstract_queue import AbstractQueue
from PSSimPy.utils.transaction_utils import settle_transaction

class System:

    def __init__(self, constraint_handler: AbstractConstraintHandler, queue: AbstractQueue):
        self.constraint_handler = constraint_handler
        self.queue = queue

    def process(self, transactions: set[Transaction]):
        txns_to_queue = set()
        # send each transaction into the constraint handler
        for transaction in transactions:
            txns_to_queue.update(self.constraint_handler.process_transaction(transaction))
        # send transactions that passed constraints into queue
        self.queue.bulk_enqueue(txns_to_queue)
        # obtain dequeued transactions to process
        txns_to_process = self.queue.begin_dequeueing()
        # process dequeued transactions
        for _ in map(settle_transaction, txns_to_process): pass

