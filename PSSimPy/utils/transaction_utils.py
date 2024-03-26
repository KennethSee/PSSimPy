from PSSimPy.utils.constants import TRANSACTION_STATUS_CODES

def settle_transaction(transaction) -> None:
    sender_account = transaction.sender_account
    recipient_account = transaction.recipient_account
    txn_amount = transaction.amount

    sender_account.balance -= txn_amount
    recipient_account.balance += txn_amount

    transaction.update_transaction_status('Success')