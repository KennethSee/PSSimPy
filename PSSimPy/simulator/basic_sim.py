import simpy
import pandas as pd
from typing import Union

from PSSimPy import System, Bank, Account, Transaction
from PSSimPy.queues import AbstractQueue, DirectQueue
from PSSimPy.credit_facilities import AbstractCreditFacility, SimplePriced
from PSSimPy.constraint_handler import AbstractConstraintHandler, PassThroughHandler
from PSSimPy.utils.logger import Logger
from PSSimPy.utils.constants import TRANSACTION_STATUS_CODES, TRANSACTION_LOGGER_HEADER
from PSSimPy.utils.time_utils import is_valid_24h_time, add_minutes_to_time, is_time_later, minutes_between
from PSSimPy.utils.file_utils import logger_file_name
from PSSimPy.utils.data_utils import initialize_classes_from_dict


class BasicSim:
    """Simulator that supports basic simulation"""

    def __init__(self,
                 name: str,
                 banks: Union[pd.DataFrame, dict[list]],
                 accounts: Union[pd.DataFrame, dict[list]],
                 transactions: Union[pd.DataFrame, dict[list]],
                 open_time: str = '08:00',
                 close_time: str = '17:00',
                 processing_window: int = 15,
                 num_days: int = 1,
                 constraint_handler: AbstractConstraintHandler = PassThroughHandler(),
                 queue: AbstractQueue = DirectQueue(),
                 credit_facility: AbstractCreditFacility = SimplePriced()):
        
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
        self.outstanding_transactions = set()
        
        # load data
        if isinstance(banks, pd.DataFrame):
            banks = banks.to_dict(orient='list')
        if isinstance(accounts, pd.DataFrame):
            accounts = accounts.to_dict(orient='list')
        if isinstance(transactions, pd.DataFrame):
            transactions = transactions.to_dict(orient='list')
        
        self._load_initial_data(banks, accounts, transactions)
        # self.account_map = self._account_mappings()
        
        # set up simulator
        self.env = simpy.Environment()
        self.env.process(self._simulate_day())
        self.system = System(constraint_handler, queue)
        
        # loggers
        self.transaction_logger = Logger(logger_file_name(name, 'processed_transactions'), TRANSACTION_LOGGER_HEADER)
        
    def _load_initial_data(self, banks_dict: dict[list], accounts_dict: dict[list], transactions_dict: dict[list]) -> None:
        # load banks
        bank_list = initialize_classes_from_dict(Bank, banks_dict)
        self.banks = {bank.name: bank for bank in bank_list}
        
        # load accounts
        accounts_revised_dict = accounts_dict.copy()
        accounts_revised_dict['owner'] = list(map(lambda x: self.banks[x], accounts_dict['owner']))
        account_list = initialize_classes_from_dict(Account, accounts_revised_dict)
        self.accounts = {account.id: account for account in account_list}
        
        # load transactions
        transactions_revised_dict = transactions_dict.copy()
        transactions_revised_dict['sender_account'] = list(map(lambda x: self.accounts[x], transactions_dict['sender_account']))
        transactions_revised_dict['receipient_account'] = list(map(lambda x: self.accounts[x], transactions_dict['receipient_account']))
        transactions_list = initialize_classes_from_dict(Transaction, transactions_revised_dict)
        transactions_list_with_time = [(transaction, transaction.time) for transaction in transactions_list]
        self.transactions = set(transactions_list_with_time)
    
    def _account_mappings(self) -> dict[str, Account]:
        # TODO implement function to get bilateral mapping of accounts that do not belong to the same bank
        pass
    
    def _simulate_day(self, day: int = 1):
        while True:
            current_time_str = add_minutes_to_time(self.open_time, self.env.now)
            period_end_time_str = add_minutes_to_time(current_time_str, self.processing_window - 1) 
            print(f'Current time: {current_time_str}')
            
            # 1. get the transactions pertaining to this time window
            curr_period_transactions = self._gather_transactions_in_window(current_time_str, period_end_time_str, self.transactions)
            self.outstanding_transactions.update(curr_period_transactions)
            
            # 2. obtain necessary intraday credit
            # TODO implement intraday credit facility
            
            # 3. outstanding transactions to be settled sent into System to be processed
            processed_transactions = self.system.process(self.outstanding_transactions)
                        
            # 5. processed transactions printed to log
            # transaction log
            transaction_to_log = {transaction for transactions in processed_transactions.values() for transaction in transactions}
            self.transaction_logger.write(self._extract_logging_details(transaction_to_log, day, current_time_str)) # settled and failed transactions
            # TODO queueu statistics log
            # TODO account balance statistics log
            # TODO transaction fees log
            
            yield self.env.timeout(self.processing_window)       
    
    def run(self):
        for _ in range(self.num_days):
            self.env.run(until=minutes_between(self.open_time, self.close_time))
            
    @staticmethod
    def _gather_transactions_in_window(begin_time: str, end_time: str, transaction_set: set[tuple[Transaction, str]]) -> set[Transaction]:
        gathered_transactions = set()
        for transaction, txn_time in transaction_set:
            if is_time_later(begin_time, txn_time) and is_time_later(txn_time, end_time):
                gathered_transactions.add(transaction)
        return gathered_transactions
        
    @staticmethod
    def _extract_logging_details(transactions: set[Transaction], day: int, time: str) -> list[tuple]:
        return [(
            day,
            time,
            transaction.sender_account.id,
            transaction.recipient_account.id,
            transaction.amount,
            'Success' if transaction.status_code == TRANSACTION_STATUS_CODES['Success'] else 'Failed'
        ) for transaction in transactions]