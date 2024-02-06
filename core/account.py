from .bank import Bank

class Account:

    def __init__(self, id: str, owner: Bank):
        self.id = id
        self.owner = owner