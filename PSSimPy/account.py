class Account:

    def __init__(self, id: str, owner, balance: float=0, posted_collateral: float = 0, **kwargs):
        self.id = id
        self.owner = owner
        self.balance = balance
        self.posted_collateral = posted_collateral
        self.txn_in = set()
        self.txn_out = set()

        # Use the kwargs to store additional user-defined attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def transfer_to(self, receipient: 'Account', amount: float) -> None:
        self.balance -= amount
        receipient.balance += amount
