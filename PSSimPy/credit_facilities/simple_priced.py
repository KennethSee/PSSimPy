from PSSimPy.credit_facilities.abstract_credit_facility import AbstractCreditFacility
from PSSimPy.account import Account


class SimplePriced(AbstractCreditFacility):
    
    def __init__(self, base_fee: float = 0, base_rate: float = 0) -> None:
        super().__init__()
        self.base_fee = base_fee
        self.base_rate = base_rate
        
    def calculate_fee(self, amount: float) -> float:
        return amount * self.base_rate + self.base_fee
    
    def lend_credit(self, account: Account, amount: float) -> float:
        self.used_credit[account.id].append(amount)
        account.balance += amount
    
    def collect_repayment(self, account: Account) -> None:
        # repay credit facility if possible
        for i, amount in enumerate(self.used_credit[account.id]):
            if amount <= account.balance:
                account.balance -= amount
                self.used_credit[account.id][i] = 0

        # remove repaid credit facility
        self.used_credit[account.id] = [cr for cr in self.used_credit[account.id] if cr != 0]