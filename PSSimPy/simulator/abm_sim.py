from random import randint
import simpy

from PSSimPy.queues import AbstractQueue, DirectQueue
from PSSimPy.transaction import Transaction
from PSSimPy.constraint_handler import AbstractConstraintHandler, PassThroughHandler
from PSSimPy.credit_facilities import AbstractCreditFacility, SimplePriced
from PSSimPy.utils.constants import TRANSACTION_STATUS_CODES
from PSSimPy.utils.time_utils import is_valid_24h_time, add_minutes_to_time, is_time_later, minutes_between

class ABMSim:
    """Simulator that supports Agent-Based Modeling"""

    def __init__(self,
                 open_time: str, # consider defaulting to 8am
                 close_time: str, # consider defaulting to 5pm
                 processing_window: int = 15, # the number of minutes between iteration
                 num_days: int = 1,
                 constraint_handler: AbstractConstraintHandler = PassThroughHandler,
                 queue: AbstractQueue = DirectQueue,
                 credit_facility: AbstractCreditFacility = SimplePriced,
                 accounts: list[dict] = None,
                 transactions: list[dict] = None # Transactions, if defined in ABM, should include time when it arrive. Time of actual settlement depends on agent's strategy.
                 ): 
        if not (is_valid_24h_time(open_time) and is_valid_24h_time(close_time)):
            raise ValueError('Invalid time input. Both open_time and close_time must be valid 24h format times.')
        self.open_time = open_time
        self.close_time = close_time
        self.processing_window = processing_window
        self.num_days = num_days
        self.constraint_handler = constraint_handler
        self.queue = queue
        self.credit_facility = credit_facility
        self.accounts = accounts
        self.transactions = transactions

        # set up simulator
        self.env = simpy.Environment()
        self.env.process(self._simulate_day(0, 1))

    def load_transactions(self, transactions: list[dict]):
        """Overwrites existing transactions if they already exist"""
        self.transactions = transactions

    def run(self):
        """Main function that executes the simulation"""
        # to implement
        for _ in range(self.num_days):
            self.env.run(until=minutes_between(self.open_time, self.close_time))

    def _simulate_day(self, txn_size_lower_bound: int, tx_size_upper_bound: int):
        while True:
            current_time_str = add_minutes_to_time(self.open_time, self.env.now)
            print(f'Current time: {current_time_str}')
            # settlement logic
            # for each account pair (exclude pairs belonging to the same bank), generate a transaction with probability p
            # generated transactions will have arrival time set as current_time_str and a random size between lower and upper bounds
            # generated transactions sent into System to be processed
            yield self.env.timeout(self.processing_window)

    # consider switching transactions to a sorted data structure for efficiency
    @staticmethod
    def _gather_transactions_in_window(begin_time: str, end_time: str, transactions_set: set[tuple[Transaction, str]]) -> set[Transaction]:
        gathered_transactions = set()
        for transaction, txn_time in transactions_set:
            if is_time_later(txn_time, begin_time, True) and not(is_time_later(txn_time, end_time, False)):
                gathered_transactions.add(transaction)
        return gathered_transactions