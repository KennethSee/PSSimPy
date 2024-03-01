from PSSimPy.bank import Bank

class Account:

    def __init__(self, id: str, owner: Bank, balance: float, **kwargs):
        self.id = id
        self.owner = owner
        self.balance = balance

        # Use the kwargs to store additional user-defined attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def transfer_to(self, receipient: 'Account', amount: float) -> None:
        self.balance -= amount
        receipient.balance += amount
