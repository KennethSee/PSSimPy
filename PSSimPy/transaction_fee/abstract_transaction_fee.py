from abc import ABC, abstractmethod
from typing import Union


class AbstractTransactionFee:

    @abstractmethod
    def calculate_fee(self, txn_amount: int, time: str, rate: Union[float, dict[float]]) -> float:
        """
        Calculates the transaction fee on a transaction.
        Can be implemented to use a static rate or variable rate (where the condition on which rate to use is indicated by the key in the rate dictionary)
        """
        pass