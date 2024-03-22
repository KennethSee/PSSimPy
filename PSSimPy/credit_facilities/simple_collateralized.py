from PSSimPy.credit_facilities.abstract_credit_facility import AbstractCreditFacility
from PSSimPy.account import Account


class SimpleCollateralized(AbstractCreditFacility):
    
    def __init__(self) -> None:
        super().__init__()
    
    def calculate_fee(self, amount: float) -> float:
        return 0.0
    
    def lend_credit(self, account: Account, amount: float) -> float:
        if amount > account.posted_collateral: return
        self.used_credit[account.id].append(amount)
        account.balance += amount
        account.posted_collateral -= amount
    
    def collect_repayment(self, account: Account) -> None:
        account.posted_collateral += self.get_total_credit(account)
        self.used_credit[account.id] = []