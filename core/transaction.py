

class Transaction:

    def __init__(self, sender_account_id: str, receiver_account_id: str, **kwargs):
        self.sender_account_id = sender_account_id
        self.receiver_account_id = receiver_account_id
        
        # Use the kwargs to store additional user-defined attributes
        for key, value in kwargs.items():
            setattr(self, key, value)