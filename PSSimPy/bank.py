class Bank:

    def __init__(self, name: str, strategy_type: str='Normal', **kwargs):
        self.name = name
        self.strategy_type = strategy_type

        # Use the kwargs to store additional user-defined attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    # only relevant for agent-based modeling
    def strategy(self, txns_to_settle: set) -> set:
        # possible relevant data:
        # - Queue
        # - Historical transaction data (perhaps just give simulator name and they can access historical transaction data from log file)
        return txns_to_settle