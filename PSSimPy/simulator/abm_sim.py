from random import randint
import simpy

from PSSimPy.bank import Bank
from PSSimPy.account import Account
from PSSimPy.queues import AbstractQueue, DirectQueue
from PSSimPy.transaction import Transaction
from PSSimPy.system import System
from PSSimPy.constraint_handler import AbstractConstraintHandler, PassThroughHandler
from PSSimPy.credit_facilities import AbstractCreditFacility, SimplePriced
from PSSimPy.utils.logger import Logger
from PSSimPy.utils.constants import TRANSACTION_STATUS_CODES, TRANSACTION_LOGGER_HEADER
from PSSimPy.utils.time_utils import is_valid_24h_time, add_minutes_to_time, is_time_later, minutes_between
from PSSimPy.utils.file_utils import logger_file_name
from PSSimPy.utils.data_utils import initialize_classes_from_dict

class ABMSim:
    """Simulator that supports Agent-Based Modeling"""

    def __init__(self,
                 name: str, # identifying name for simulation
                 banks: dict[list],
                 accounts: dict[list],
                 transactions: dict[list] = None, # Transactions, if defined in ABM, should include time when it arrive. Time of actual settlement depends on agent's strategy.
                 open_time: str = '08:00',
                 close_time: str = '17:00',
                 processing_window: int = 15, # the number of minutes between iteration
                 num_days: int = 1,
                 constraint_handler: AbstractConstraintHandler = PassThroughHandler,
                 queue: AbstractQueue = DirectQueue,
                 credit_facility: AbstractCreditFacility = SimplePriced
                 ): 
        if not (is_valid_24h_time(open_time) and is_valid_24h_time(close_time)):
            raise ValueError('Invalid time input. Both open_time and close_time must be valid 24h format times.')
        self.name = name
        self.open_time = open_time
        self.close_time = close_time
        self.processing_window = processing_window
        self.num_days = num_days
        self.constraint_handler = constraint_handler
        self.queue = queue
        self.credit_facility = credit_facility
        
        # load data
        self._load_initial_data(banks, accounts, transactions)

        # set up simulator
        self.env = simpy.Environment()
        self.env.process(self._simulate_day())
        self.system = System(constraint_handler, queue)

        # loggers
        self.transaction_logger = Logger(logger_file_name(name, 'processed_transactions'), TRANSACTION_LOGGER_HEADER)

    def load_transactions(self, transactions: list[dict]):
        """Overwrites existing transactions if they already exist"""
        self.transactions = transactions

    def run(self):
        """Main function that executes the simulation"""
        # to implement
        for _ in range(self.num_days):
            self.env.run(until=minutes_between(self.open_time, self.close_time))

    def _simulate_day(self, day: int=1, txn_size_lower_bound: int=0, tx_size_upper_bound: int=100):
        while True:
            current_time_str = add_minutes_to_time(self.open_time, self.env.now)
            print(f'Current time: {current_time_str}')
            # settlement logic
            # 1. for each account pair (exclude pairs belonging to the same bank), generate a transaction with probability p and add to outstanding transactions
            # generated transactions will have arrival time set as current_time_str and a random size between lower and upper bounds
            # 2. go through outstanding transaction list and identify transactions to settle in current period based on bank strategy
            # 3. obtain necessary intraday credit
            # 4. identified transactions to be settled sent into System to be processed
            transactions_to_log = self.system.process(transactions_to_settle)
            # 5. processed transactions printed to log
            self.transaction_logger.write(self._extract_logging_details(transactions_to_log, day, current_time_str))

            # end of period
            yield self.env.timeout(self.processing_window)

    # consider switching transactions to a sorted data structure for efficiency
    @staticmethod
    def _gather_transactions_in_window(begin_time: str, end_time: str, transactions_set: set[tuple[Transaction, str]]) -> set[Transaction]:
        gathered_transactions = set()
        for transaction, txn_time in transactions_set:
            if is_time_later(txn_time, begin_time, True) and not(is_time_later(txn_time, end_time, False)):
                gathered_transactions.add(transaction)
        return gathered_transactions
    
    @staticmethod
    def _extract_logging_details(transactions: set[Transaction], day: int, time: str) -> list[tuple]:
        return [
            (
                day,
                time,
                transaction.sender_account.id,
                transaction.receipient_account.id,
                transaction.amount,
                'Success' if transaction.status_code == TRANSACTION_STATUS_CODES['Success'] else 'Failed'
            )
            for transaction in transactions
        ]
    
    def _load_initial_data(self, banks_dict: dict, accounts_dict: dict, transactions_dict: dict):
        # load bank data
        banks_list = initialize_classes_from_dict(Bank, banks_dict)
        self.banks = {bank.name: bank for bank in banks_list}
        # load accounts data
        accounts_revised_dict = accounts_dict.copy()
        accounts_revised_dict['owner'] = list(map(lambda x: self.banks[x], accounts_dict['owner']))
        accounts_list = initialize_classes_from_dict(Account, accounts_revised_dict)
        self.accounts = {account.id: account for account in accounts_list}
        # load transactions data
        if transactions_dict is not None:
            transactions_revised_dict = transactions_dict.copy()
            transactions_revised_dict['sender_account'] = list(map(lambda x: self.accounts[x], transactions_dict['sender_account']))
            transactions_revised_dict['receipient_account'] = list(map(lambda x: self.accounts[x], transactions_dict['receipient_account']))
            transactions_list = initialize_classes_from_dict(Transaction, transactions_revised_dict)
            transactions_list_with_time = [(transaction, transaction.time) for transaction in transactions_list]
            self.transactions = set(transactions_list_with_time)

