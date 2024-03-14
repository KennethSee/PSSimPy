from PSSimPy.transaction_fee.abstract_transaction_fee import AbstractTransactionFee


class FixedTransactionFee(AbstractTransactionFee):

    def __init__(self):
        super().__init__()

    @staticmethod
    def calculate_fee(txn_amount: int, time: str, rate: float) -> float:
        return txn_amount * rate