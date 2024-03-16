from random import randint
from typing import Union
import simpy
import pandas as pd
from collections import defaultdict

from PSSimPy.bank import Bank
from PSSimPy.account import Account
from PSSimPy.queues import AbstractQueue, DirectQueue
from PSSimPy.transaction import Transaction
from PSSimPy.system import System
from PSSimPy.transaction_fee import AbstractTransactionFee, FixedTransactionFee
from PSSimPy.constraint_handler import AbstractConstraintHandler, PassThroughHandler
from PSSimPy.credit_facilities import AbstractCreditFacility, SimplePriced
from PSSimPy.utils.logger import Logger
from PSSimPy.utils.constants import TRANSACTION_STATUS_CODES, TRANSACTION_LOGGER_HEADER, TRANSACTION_FEE_LOGGER_HEADER
from PSSimPy.utils.time_utils import is_valid_24h_time, add_minutes_to_time, is_time_later, minutes_between
from PSSimPy.utils.file_utils import logger_file_name
from PSSimPy.utils.data_utils import initialize_classes_from_dict

class ABMSim:
    """Simulator that supports Agent-Based Modeling"""

    def __init__(self,
                 name: str, # identifying name for simulation
                 banks: Union[pd.DataFrame, dict[list]],
                 accounts: Union[pd.DataFrame, dict[list]],
                 transactions: Union[pd.DataFrame, dict[list]] = None, # Transactions, if defined in ABM, should include time when it arrive. Time of actual settlement depends on agent's strategy.
                 open_time: str = '08:00',
                 close_time: str = '17:00',
                 processing_window: int = 15, # the number of minutes between iteration
                 num_days: int = 1,
                 constraint_handler: AbstractConstraintHandler = PassThroughHandler(),
                 queue: AbstractQueue = DirectQueue(),
                 credit_facility: AbstractCreditFacility = SimplePriced(),
                 transaction_fee_handler: AbstractTransactionFee = FixedTransactionFee(),
                 transaction_fee_rate: Union[float, dict[float]] = 0.0,
                 bank_failure: dict[list[tuple[str, str]]] = None # key is day and value is a tuple of time and bank name
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
        self.account_map = self._account_mappings()

        # set up simulator
        self.env = simpy.Environment()
        self.env.process(self._simulate_day())
        self.system = System(constraint_handler, queue)

        # loggers
        self.transaction_logger = Logger(logger_file_name(name, 'processed_transactions'), TRANSACTION_LOGGER_HEADER)
        self.transaction_fee_logger = Logger(logger_file_name(name, 'transaction_fees'), TRANSACTION_FEE_LOGGER_HEADER)

    def load_transactions(self, transactions_dict: list[dict]):
        """Overwrites existing transactions if they already exist"""
        transactions_revised_dict = transactions_dict.copy()
        transactions_revised_dict['sender_account'] = list(map(lambda x: self.accounts[x], transactions_dict['sender_account']))
        transactions_revised_dict['receipient_account'] = list(map(lambda x: self.accounts[x], transactions_dict['receipient_account']))
        transactions_list = initialize_classes_from_dict(Transaction, transactions_revised_dict)
        transactions_list_with_time = [(transaction, transaction.time) for transaction in transactions_list]
        self.transactions = set(transactions_list_with_time)

    def run(self):
        """Main function that executes the simulation"""
        # repeate simulation for each day
        for _ in range(self.num_days):
            self.env.run(until=minutes_between(self.open_time, self.close_time))
            # EOD handling - not implemented for now

    def _simulate_day(self, day: int=1, txn_size_lower_bound: int=0, tx_size_upper_bound: int=100):
        while True:
            current_time_str = add_minutes_to_time(self.open_time, self.env.now)
            period_end_time_str = add_minutes_to_time(current_time_str, self.processing_window - 1)
            print(f'Current time: {current_time_str}')
            # check if any bank fails in this time period
            self._update_failed_banks(day, current_time_str, period_end_time_str)

            # settlement logic
            if self.transactions is None:
                # 1a. for each account pair (exclude pairs belonging to the same bank), generate a transaction with probability p and add to outstanding transactions
                # generated transactions will have arrival time set as current_time_str and a random size between lower and upper bounds
                pass
            else:
                # 1b. get the transactions pertaining to this time window
                curr_period_transactions = self._gather_transactions_in_window(current_time_str, period_end_time_str, self.transactions)
                self.outstanding_transactions.update(curr_period_transactions)
            # 2. go through outstanding transaction list and identify transactions to settle in current period based on bank strategy
            # remove outstanding transactions where a failed bank is involved
            txns_failed_from_bank_failure = {transaction for transaction in self.outstanding_transactions if transaction.involves_failed_bank()}
            for transaction in txns_failed_from_bank_failure:
                transaction.status_code = TRANSACTION_STATUS_CODES['Failed']
            self.outstanding_transactions -= txns_failed_from_bank_failure
            # proceed with identifying transactions to settle
            transactions_to_settle = set()
            for bank_name, bank in self.banks.items():
                bank_oustanding_transactions = {transaction for transaction in self.outstanding_transactions if transaction.receipient_account.owner.name == bank_name}
                transactions_to_settle.update(bank.strategy(bank_oustanding_transactions, self.name, current_time_str, self.queue))
            self.outstanding_transactions -= transactions_to_settle # remove transactions being settled from outstanding transactions set
            # 3. obtain necessary intraday credit
            liquidity_requirement = defaultdict(float)
            
            for txn in curr_period_transactions:
                liquidity_requirement[txn.sender_account] += txn.amount
                
            for acc, requirement in liquidity_requirement.items():
                credit_amount = requirement - acc.balance
                if credit_amount > 0:
                    self.credit_facility.lend_credit(acc, credit_amount)
            # 4. identified transactions to be settled sent into System to be processed
            processed_transactions = self.system.process(transactions_to_settle)
            transactions_to_log = {transaction for transactions in processed_transactions.values() for transaction in transactions} # merge the settled and failed transactions
            transactions_to_log.update(txns_failed_from_bank_failure) # add the failed transactions due to bank failure

            # extract transaction fees from successful transactions
            transaction_fees = [(transaction.sender_account.id, day, current_time_str, self.transaction_fee_handler.calculate_fee(transaction.amount, current_time_str, self.transaction_fee_rate)) 
                                for transaction in processed_transactions['Processed']]
            # 5. processed transactions printed to log
            self.transaction_logger.write(self._extract_logging_details(transactions_to_log, day, current_time_str)) # settled and failed transactions
            # aggregate queue statistics
            # account balance statistics
            # transaction fees
            self.transaction_fee_logger.write(transaction_fees)
            # transactions arrival (ONLY IF TRANSACTIONS ARE MODELED TO BE RANDOM)

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
    
    def _load_initial_data(self, banks_dict: dict, accounts_dict: dict, transactions_dict: dict, strategy_mapping: dict=None):
        # load bank data
        banks_list = initialize_classes_from_dict(Bank, banks_dict)
        self.banks = {bank.name: bank for bank in banks_list}
        if strategy_mapping is not None:
            for bank_name, bank in self.banks.items():
                # update bank to use the appropriate class according to their defined strategies
                bank_strategy = bank.strategy
                if bank_strategy != 'Normal':
                    bank_attrs = vars(bank)
                    updated_bank = strategy_mapping[bank_strategy](**bank_attrs)
                    self.banks[bank_name] = updated_bank
        # load accounts data
        accounts_revised_dict = accounts_dict.copy()
        accounts_revised_dict['owner'] = list(map(lambda x: self.banks[x], accounts_dict['owner']))
        accounts_list = initialize_classes_from_dict(Account, accounts_revised_dict)
        self.accounts = {account.id: account for account in accounts_list}
        # load transactions data
        if transactions_dict is not None:
            self.load_transactions(transactions_dict)

    # current implementation is O(n^2). Possible to optimize?
    def _account_mappings(self):
        """
        Get bilateral mapping of accounts that do not belong to the same bank.
        """
        bilateral_mappings = set()
        accounts = self.accounts.values()
        # Iterate through each account
        for i, account_a in enumerate(accounts):
            for account_b in list(accounts)[i+1:]:
                # Check if the accounts belong to different banks
                if account_a.owner.name != account_b.owner.name:
                    # Add the mapping to the set, ensuring account_a's id is always lower to avoid duplicates
                    mapping = tuple(sorted((account_a.id, account_b.id), key=str))
                    bilateral_mappings.add(mapping)
        return bilateral_mappings
    
    def _update_failed_banks(self, day, begin_time, end_time):
        if self.bank_failure is not None and day in self.bank_failure:
            failures_to_check = self.bank_failure[day]
            for time, bank_name in failures_to_check:
                if is_time_later(time, begin_time, True) and not(is_time_later(time, end_time, False)):
                    # update bank status to failed
                    self.banks[bank_name].is_failed = True

