from PSSimPy.account import Account

from PSSimPy.utils.constants import TRANSACTION_STATUS_CODES
from PSSimPy.utils.account_utils import is_failed_account


class Transaction:

    # Class attribute to hold references to all instances
    _instances = set()

    def __new__(cls, *args, **kwargs):
        # Create a new instance
        instance = super().__new__(cls)
        # Add the new instance to the set of instances
        cls._instances.add(instance)
        return instance

    def __init__(self, sender_account: Account, recipient_account: Account, amount: float, priority: int=1, **kwargs):
        self.sender_account = sender_account
        self.recipient_account = recipient_account
        self.amount = amount
        self.priority = priority
        self.status_code = TRANSACTION_STATUS_CODES['Open']
        
        # Use the kwargs to store additional user-defined attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
        # set default value for day and time
        self.day = kwargs.get('day', 1)
        self.time = kwargs.get('time', None)
        self.arrival_day = kwargs.get('day', 1)
        self.arrival_time = kwargs.get('time', None)
        # set default value for submission and settle day and time
        self.submission_day = kwargs.get('submission_day', None)
        self.submission_time = kwargs.get('submission_time', None)
        self.settle_day = kwargs.get('settle_day', None)
        self.settle_time = kwargs.get('settle_time', None)

    def update_transaction_status(self, status: str):
        try:
            self.status_code = TRANSACTION_STATUS_CODES[status]
        except KeyError:
            print(f"Invalid status: '{status}'. Please provide a valid transaction status.")

    def involves_failed_bank(self) -> bool:
        """Checks if either the sender or recipient accounts belongs to a failed bank"""
        return is_failed_account(self.sender_account) or is_failed_account(self.recipient_account)

    @classmethod
    def get_instances(cls):
        """Provides the set of all created transactions"""
        return cls._instances

    @classmethod
    def clear_instances(cls):
        """Clears tracked transactions created. Should be used before running a new simulation."""
        cls._instances.clear()
