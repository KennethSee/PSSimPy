from .abstract_settlement_mechansim import AbstractSettlementMechanism
from ..core.transaction import Transaction

class SimpleRTGS(AbstractSettlementMechanism):

    def settle_transaction(self, transaction: Transaction):
        sender = transaction.sender_account
        receipient = transaction.receipient_account
        # check if sender has sufficient account balance
        if sender.balance - transaction.amount >= 0:
            sender.transfer_to(receipient, transaction.amount)
            transaction.update_transaction_status('Success')
        else:
            transaction.update_transaction_status('Failed')