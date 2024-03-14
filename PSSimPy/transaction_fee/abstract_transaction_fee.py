from abc import ABC, abstractmethod


class AbstractTransactionFee:

    @staticmethod
    @abstractmethod
    def calculate_fee(txn_amount: int, time: str, rate: float | dict) -> float:
        """
        Calculates the transaction fee on a transaction.
        Can be implemented to use a static rate or variable rate (where the condition on which rate to use is indicated by the key in the rate dictionary)
        """
        pass