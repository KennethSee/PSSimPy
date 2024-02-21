from PSSimPy.constraint_handler import AbstractConstraintHandler, PassThroughHandler
from PSSimPy.queues import AbstractQueue, DirectQueue
from PSSimPy.credit_facilities import AbstractCreditFacility, SimplePriced
from PSSimPy.utils.constants import TRANSACTION_STATUS_CODES
from PSSimPy.utils.time_utils import is_valid_24h_time, add_minutes_to_time

class ABMSim:
    """Simulator that supports Agent-Based Modeling"""

    def __init__(self,
                 open_time: str, # consider defaulting to 8am
                 close_time: str, # consider defaulting to 5pm
                 processing_window: int = 5, # the number of minutes between iteration
                 num_days: int = 1,
                 constraint_handler: AbstractConstraintHandler = PassThroughHandler,
                 queue: AbstractQueue = DirectQueue,
                 credit_facility: AbstractCreditFacility = SimplePriced,
                 accounts: list[dict] = None,
                 transactions: list[dict] = None # Transactions, if defined in ABM, should include time when it arrive. Time of actual settlement depends on agent's strategy.
                 ): 
        if not (is_valid_24h_time(open_time) or is_valid_24h_time(close_time)):
            return 'Invalid time input'
        self.open_time = open_time
        self.close_time = close_time
        self.processing_window = processing_window
        self.num_days = num_days
        self.constraint_handler = constraint_handler
        self.queue = queue
        self.credit_facility = credit_facility
        self.accounts = accounts
        self.transactions = transactions

    def load_transactions(self, transactions: list[dict]):
        """Overwrites existing transactions if they already exist"""
        self.transactions = transactions

    def run(self):
        """Main function that executes the simulation"""
        pass