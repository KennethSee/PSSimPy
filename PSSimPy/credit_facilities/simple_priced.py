from PSSimPy.credit_facilities.abstract_credit_facility import AbstractCreditFacility
from PSSimPy.account import Account


class SimplePriced(AbstractCreditFacility):
    
    def __init__(self, price: float = 0, rate: float = 0) -> None:
        super().__init__()
        self.price = price
        self.rate = rate
    
    def lend_credit(self, account: Account, amount: float) -> float:
        account.balance += amount
        self.total_credit[account.id] += amount
        self.total_fee[account.id] += (amount * self.rate) + self.price
    
    def collect_repayment(self, account: Account) -> None:
        if self.get_total_credit_and_fee(account) >= account.balance:
            return
        account.balance -= self.total_credit[account.id]
        account.balance -= self.total_fee[account.id]
        self.total_credit[account.id] = 0
        self.total_fee[account.id] = 0