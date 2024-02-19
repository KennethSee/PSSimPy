from PSSimPy.account import Account
from PSSimPy.utils import TRANSACTION_STATUS_CODES

class Transaction:

    def __init__(self, sender_account: Account, receipient_account: Account, amount: float, priority: int=1, **kwargs):
        self.sender_account = sender_account
        self.receipient_account = receipient_account
        self.amount = amount
        self.priority = priority
        self.status_code = TRANSACTION_STATUS_CODES['Open']
        
        # Use the kwargs to store additional user-defined attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update_transaction_status(self, status: str):
        try:
            self.status_code = TRANSACTION_STATUS_CODES[status]
        except KeyError:
            print(f"Invalid status: '{status}'. Please provide a valid transaction status.")
