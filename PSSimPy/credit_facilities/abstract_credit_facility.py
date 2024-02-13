from PSSimPy.account import Account
from abc import ABC, abstractmethod

class AbstractCreditFacility(ABC):
        
    @abstractmethod
    def lend_credit(self, amount: float, account: Account) -> float:
        pass
    
    @abstractmethod
    def get_credit_amount(self, account: Account) -> float:
        pass
    
    @abstractmethod
    def get_total_fee(self, account: Account) -> float:
        pass
    
    @abstractmethod
    def collect_repayment(self, accounts: list[Account]) -> None:
        pass