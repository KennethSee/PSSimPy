from PSSimPy.account import Account

def min_balance_maintained(sender_account: Account, txn_amount: float, min_balance: float=0) -> bool:
    return sender_account.balance - txn_amount >= min_balance

def is_failed_account(account: Account) -> bool:
    return account.owner.is_failed

def load_account_with_transactions(account: Account, transactions: set):
    txn_in = set()
    txn_out = set()
    for transaction in transactions:
        if transaction.sender_account.id == account.id:
            txn_out.add(transaction)
        elif transaction.receipient_account.id == account.id:
            txn_in.add(transaction)
    account.txn_in.update(txn_in)
    account.txn_out.update(txn_out)