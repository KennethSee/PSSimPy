from PSSimPy.bank import Bank

class Account:

    def __init__(self, id: str, owner: Bank, balance: float):
        self.id = id
        self.owner = owner
        self.balance = balance

    def transfer_to(self, receipient: 'Account', amount: float) -> None:
        self.balance -= amount
        receipient.balance += amount