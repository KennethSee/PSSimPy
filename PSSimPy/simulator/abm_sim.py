from PSSimPy.constraint_handler import AbstractConstraintHandler, PassThroughHandler
from PSSimPy.queues import AbstractQueue, DirectQueue
from PSSimPy.credit_facilities import AbstractCreditFacility, SimplePriced
from PSSimPy.utils import TRANSACTION_STATUS_CODES

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
        pass

    def load_transactions(self, transactions: list[dict]):
        """Overwrites existing transactions if they already exist"""
        self.transactions = transactions