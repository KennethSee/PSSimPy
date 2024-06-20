from PSSimPy.credit_facilities.abstract_credit_facility import AbstractCreditFacility
from PSSimPy.account import Account


class SimpleCollateralized(AbstractCreditFacility):
    
    def __init__(self) -> None:
        super().__init__()
    
    def calculate_fee(self, amount: float) -> float:
        return 0.0
    
    def lend_credit(self, account: Account, amount: float) -> float:
        if amount > account.posted_collateral: return 0.0
        self.used_credit[account.id].append(amount)
        account.balance += amount
        account.posted_collateral -= amount
    
    def collect_repayment(self, account: Account) -> None:
        # repay credit facility if possible
        for i, amount in enumerate(self.used_credit[account.id]):
            if amount <= account.balance:
                account.balance -= amount
                account.posted_collateral += amount
                self.used_credit[account.id][i] = 0

        # remove repaid credit facility
        self.used_credit[account.id] = [cr for cr in self.used_credit[account.id] if cr != 0]