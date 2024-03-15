from PSSimPy.transaction_fee.abstract_transaction_fee import AbstractTransactionFee


class FixedTransactionFee(AbstractTransactionFee):

    def __init__(self):
        super().__init__()

    def calculate_fee(self, txn_amount: int, time: str, rate: float) -> float:
        return txn_amount * rate