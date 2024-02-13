from PSSimPy.account import Account

class SimplePriced:
    
    def __init__(self, price: float, rate:float) -> None:
        self.price = price
        self.total_credit = {}
        self.total_fee = {}
    
    def lend_credit(self, amount: float, account: Account) -> float:
        if self.total_fee[account.id] is None:
            self.total_fee[account.id] = 0
            self.total_credit[account.id] = 0
        else:
            self.total_fee[account.id] += self.price
            self.total_credit[account.id] += amount
        return amount
    
    def get_credit_amount(self, account: Account) -> float:
        return self.total_fee[account.id]
    
    def get_total_fee(self, account: Account) -> float:
        return self.total_fee[account.id]
    
    def collect_repayment(self, accounts: list[Account]) -> None:
        for account in accounts:
            account.balance -= self.total_credit[account.id]
            account.balance -= self.total_fee[account.id]
            self.total_credit[account.id] = 0
            self.total_fee[account.id] = 0
        return None