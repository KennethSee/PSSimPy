from PSSimPy.account import Account

def min_balance_maintained(sender_account: Account, txn_amount: float, min_balance: float=0) -> bool:
    return sender_account.balance - txn_amount >= min_balance

def is_failed_account(account: Account) -> bool:
    return account.owner.is_failed