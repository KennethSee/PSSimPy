import simpy
import pandas as pd
from typing import Union, Dict, List, Tuple, Set
from collections import defaultdict

from PSSimPy import System, Bank, Account, Transaction
from PSSimPy.queues import AbstractQueue, DirectQueue
from PSSimPy.credit_facilities import AbstractCreditFacility, SimplePriced
from PSSimPy.constraint_handler import AbstractConstraintHandler, PassThroughHandler
from PSSimPy.transaction_fee import AbstractTransactionFee, FixedTransactionFee
from PSSimPy.utils.logger import Logger
from PSSimPy.utils.constants import TRANSACTION_STATUS_CODES, TRANSACTION_LOGGER_HEADER, TRANSACTION_FEE_LOGGER_HEADER, \
    QUEUE_STATS_HEADER, ACCOUNT_BALANCE_HEADER, CREDIT_FACILITY_LOGGER_HEADER
from PSSimPy.utils.time_utils import is_valid_24h_time, add_minutes_to_time, is_time_later, minutes_between
from PSSimPy.utils.file_utils import logger_file_name
from PSSimPy.utils.data_utils import initialize_classes_from_dict
from PSSimPy.utils.account_utils import load_account_with_transactions


class BasicSim:
    """Simulator that supports basic simulation"""

    def __init__(self,
                 name: str,
                 banks: Union[pd.DataFrame, Dict[str, List]],
                 accounts: Union[pd.DataFrame, Dict[str, List]],
                 transactions: Union[pd.DataFrame, Dict[str, List]],
                 open_time: str = '08:00',
                 close_time: str = '17:00',
                 processing_window: int = 15,
                 num_days: int = 1,
                 constraint_handler: AbstractConstraintHandler = PassThroughHandler(),
                 queue: AbstractQueue = DirectQueue(),
                 credit_facility: AbstractCreditFacility = SimplePriced(),
                 transaction_fee_handler: AbstractTransactionFee = FixedTransactionFee(),
                 transaction_fee_rate: Union[float, Dict[str, float]] = 0.0,
                 bank_failure: Dict[int, List[Tuple[str, str]]] = None, # key is day and value is a tuple of time and bank name
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
        self.transaction_fee_handler = transaction_fee_handler
        self.transaction_fee_rate = transaction_fee_rate
        self.bank_failure = bank_failure
        self.outstanding_transactions = set()
        
        # load data
        if isinstance(banks, pd.DataFrame):
            banks = banks.to_dict(orient='list')
        if isinstance(accounts, pd.DataFrame):
            accounts = accounts.to_dict(orient='list')
        if isinstance(transactions, pd.DataFrame):
            transactions = transactions.to_dict(orient='list')
        
        self._load_initial_data(banks, accounts, transactions)
        
        # setup system
        self.system = System(constraint_handler, queue)
        
        # setup loggers
        self.transaction_logger = Logger(logger_file_name(name, 'processed_transactions'), TRANSACTION_LOGGER_HEADER)
        self.transaction_fee_logger = Logger(logger_file_name(name, 'transaction_fees'), TRANSACTION_FEE_LOGGER_HEADER)
        self.queue_stats_logger = Logger(logger_file_name(name, 'queue_stats'), QUEUE_STATS_HEADER)
        self.account_balance_logger = Logger(logger_file_name(name, 'account_balance'), ACCOUNT_BALANCE_HEADER)
        self.credit_facility_logger = Logger(logger_file_name(name, 'credit_facility'), CREDIT_FACILITY_LOGGER_HEADER)
        
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
        transactions_list_with_time = [(transaction, transaction.day, transaction.time) for transaction in transactions_list]
        self.transactions = set(transactions_list_with_time)
    
    def _simulate_day(self, day: int = 1):
        while True:
            current_time_str = add_minutes_to_time(self.open_time, self.env.now)
            period_end_time_str = add_minutes_to_time(current_time_str, self.processing_window - 1) 
            self._update_failed_banks(day, current_time_str, period_end_time_str)
            
            # 1. get the transactions pertaining to this time window
            curr_period_transactions = self._gather_transactions_in_window(day, current_time_str, period_end_time_str, self.transactions)
            for account in self.accounts.values():
                load_account_with_transactions(account, curr_period_transactions)
            self.outstanding_transactions.update(curr_period_transactions)
            # -> remove transactions from failed banks
            txns_failed_from_bank_failure = {transaction for transaction in self.outstanding_transactions if transaction.involves_failed_bank()}
            for transaction in txns_failed_from_bank_failure:
                transaction.status_code = TRANSACTION_STATUS_CODES['Failed']
            self.outstanding_transactions -= txns_failed_from_bank_failure
            
            # 2. obtain necessary intraday credit
            liquidity_requirement = defaultdict(float)
            # -> calculate liquidity requirements for all outstanding transactions
            for txn in curr_period_transactions:
                liquidity_requirement[txn.sender_account] += txn.amount
            # -> lend required credit                
            for acc, requirement in liquidity_requirement.items():
                credit_amount = requirement - acc.balance
                if credit_amount > 0:
                    self.credit_facility.lend_credit(acc, credit_amount)
            
            # 3. outstanding transactions to be settled sent into System to be processed
            processed_transactions = self.system.process(curr_period_transactions)
            # -> calculate transaction fees
            transaction_fees = [(transaction.sender_account.id, day, current_time_str, self.transaction_fee_handler.calculate_fee(transaction.amount, current_time_str, self.transaction_fee_rate)) 
                                for transaction in processed_transactions['Processed']]
            
            # 5. processed transactions printed to log
            # -> transaction log
            transaction_to_log = {transaction for transactions in processed_transactions.values() for transaction in transactions}
            self.transaction_logger.write(self._extract_logging_details(transaction_to_log, day, current_time_str)) # settled and failed transactions
            # -> queueu statistics log
            self.queue_stats_logger.write([(day, current_time_str, self.queue.get_num_txns(), self.queue.get_txn_amount_total())])
            # -> account balance statistics log
            self.account_balance_logger.write([(day, current_time_str, account.id, account.balance) for account in self.accounts.values()])
            # -> transaction fees log
            self.transaction_fee_logger.write(transaction_fees)
            # -> credit facility usage log
            self.credit_facility_logger.write([
                (day, current_time_str, account.id, account.posted_collateral, self.credit_facility.get_total_credit(account), self.credit_facility.get_total_fee(account))
                for account in self.accounts.values()
            ])
            
            yield self.env.timeout(self.processing_window)       
    
    def run(self):
        """Main function that executes the simulation"""
        # repeate simulation for each day
        for i in range(self.num_days):
            self.env = simpy.Environment()
            self.env.process(self._simulate_day(i+1))
            self.env.run(until=minutes_between(self.open_time, self.close_time))
            self.credit_facility.collect_all_repayment(self.accounts.values())
            # TODO EOD handling - not implemented for now
            
    @staticmethod
    def _gather_transactions_in_window(day: int, begin_time: str, end_time: str, transactions_set: Set[Tuple[Transaction, int, str]]) -> Set[Transaction]:
        gathered_transactions = set()
        for transaction, txn_day, txn_time in transactions_set:
            if txn_day == day and (is_time_later(txn_time, begin_time, True) and not(is_time_later(txn_time, end_time, False))):
                gathered_transactions.add(transaction)
        return gathered_transactions
        
    @staticmethod
    def _extract_logging_details(transactions: Set[Transaction], day: int, time: str) -> List[Tuple]:
        return [(
            day,
            time,
            transaction.sender_account.id,
            transaction.receipient_account.id,
            transaction.amount,
            'Success' if transaction.status_code == TRANSACTION_STATUS_CODES['Success'] else 'Failed'
        ) for transaction in transactions]
    
    def _update_failed_banks(self, day, begin_time, end_time):
        if self.bank_failure is not None and day in self.bank_failure:
            failures_to_check = self.bank_failure[day]
            for time, bank_name in failures_to_check:
                if is_time_later(time, begin_time, True) and not(is_time_later(time, end_time, False)):
                    # update bank status to failed
                    self.banks[bank_name].is_failed = True