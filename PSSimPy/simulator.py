from PSSimPy.constraint_handler import AbstractConstraintHandler
from PSSimPy.queues import AbstractQueue, DirectQueue
from PSSimPy.credit_facilities import AbstractCreditFacility
from PSSimPy.utils import TRANSACTION_STATUS_CODES


class BasicSim:

    def __init__(self,
                 open_time: str,
                 close_time: str,
                 num_days: int,
                 settlement_mechanism: AbstractConstraintHandler,
                 queue: AbstractQueue,
                 credit_facility: AbstractCreditFacility,
                 accounts: list[dict] = None,
                 transactions: list[dict] = None):
        
        self.open_time = open_time
        self.close_time = close_time
        self.num_days = num_days
        self.settlement_mechanism = settlement_mechanism
        self.queue = queue
        self.credit_facility = credit_facility
        self.part_accounts = []
        self.txn_submitted = []
        self.txn_processed = []
        
        if accounts is not None:
            self.load_accounts(accounts)

        if transactions is not None:
            self.load_txn(transactions)
        
    def run_simulation(self) -> None:
        if len(self.part_accounts) == 0:
            raise Exception("No accounts loaded in the simulator")
        
        if len(self.txn_submitted) == 0:
            raise Exception("No transactions loaded in the simulator.")
        
        for trx in self.txn_submitted:
            self.settlement_mechanism.process_transaction(trx)
            
            if trx.status_code == TRANSACTION_STATUS_CODES['Failed']:
                self.credit_facility.lend_credit(trx.amount, trx.sender_account)
            
            self.settlement_mechanism.settle_transaction(trx)
            
            self.txn_processed.append(trx)
        
        self.credit_facility.collect_repayment(self.part_accounts)     
        
    def load_accounts(self, accounts: list[dict]) -> None:
        self.part_accounts.extend(accounts)
    
    def load_txn(self, transactions: list[dict]) -> None:
        self.txn_submitted.extend(transactions)