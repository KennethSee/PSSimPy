from PSSimPy.credit_facilities.abstract_credit_facility import AbstractCreditFacility
from PSSimPy.account import Account


class SimplePriced(AbstractCreditFacility):
    
    def __init__(self, base_fee: float = 0, base_rate: float = 0) -> None:
        super().__init__()
        self.base_fee = base_fee
        self.base_rate = base_rate
        
    def calculate_fee(self, credit_amount: float) -> float:
        return credit_amount * self.base_rate + self.base_fee
    
    def lend_credit(self, account: Account, amount: float) -> float:
        self.used_credit[account.id].append(amount)
        account.balance += amount
    
    def collect_repayment(self, account: Account) -> None:
        for i, credit_amount in enumerate(self.used_credit[account.id]):
            fee = self.calculate_fee(credit_amount)
            
            if credit_amount + fee <= account.balance:
                account.balance -= (credit_amount + fee)
                self.used_credit[account.id][i] = 0
        
        self.used_credit[account.id] = [x for x in self.used_credit[account.id] if x != 0]