from abc import ABC, abstractmethod
from ..core.transaction import Transaction

class AbstractSettlementMechanism(ABC):
    
    @abstractmethod
    def settle_transaction(self, transaction: Transaction):
        pass