from PSSimPy.queues.abstract_queue import AbstractQueue

class Bank:

    def __init__(self, name: str, strategy_type: str='Normal', **kwargs):
        self.name = name
        self.strategy_type = strategy_type

        # Use the kwargs to store additional user-defined attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    # only relevant for agent-based modeling
    def strategy(self, txns_to_settle: set, sim_name: str, current_time: str, queue: AbstractQueue) -> set:
        return txns_to_settle