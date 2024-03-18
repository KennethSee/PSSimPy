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
        repaid_amount = 0
        
        for i, credit_amount in enumerate(self.used_credit[account.id]):
            if credit_amount <= account.balance:
                account.balance -= credit_amount
                repaid_amount += credit_amount
                self.used_credit[account.id][i] = 0
        
        self.used_credit[account.id] = [x for x in self.used_credit[account.id] if x != 0]
        account.posted_collateral += repaid_amount