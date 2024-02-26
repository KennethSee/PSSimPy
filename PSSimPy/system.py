from PSSimPy.transaction import Transaction
from PSSimPy.constraint_handler.abstract_constraint_handler import AbstractConstraintHandler
from PSSimPy.queues.abstract_queue import AbstractQueue
from PSSimPy.utils.transaction_utils import settle_transaction
from PSSimPy.utils.constants import TRANSACTION_STATUS_CODES

class System:

    def __init__(self, constraint_handler: AbstractConstraintHandler, queue: AbstractQueue):
        self.constraint_handler = constraint_handler
        self.queue = queue

    def process(self, transactions: set[Transaction]) -> dict:
        txns_to_queue = set()
        # send each transaction into the constraint handler
        for transaction in transactions:
            self.constraint_handler.process_transaction(transaction)
            txns_to_queue.update(self.constraint_handler.get_passed_transactions())
        self.constraint_handler.clear()
        # send transactions that passed constraints into queue
        self.queue.bulk_enqueue(txns_to_queue)
        # obtain dequeued transactions to process
        txns_to_process = self.queue.begin_dequeueing()
        # process dequeued transactions
        for _ in map(settle_transaction, txns_to_process): pass
        # get failed transactions
        failed_transactions = [transaction for transaction in transactions if transaction.status_code==TRANSACTION_STATUS_CODES['Failed']]

        # return processed transactions
        return {'Processed': txns_to_process, 'Failed': failed_transactions}

