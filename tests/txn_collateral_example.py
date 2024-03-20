import pandas as pd
from PSSimPy.simulator import BasicSim
from PSSimPy.account import Account
from PSSimPy.credit_facilities import AbstractCreditFacility, SimpleCollateralized
from PSSimPy.constraint_handler import MinBalanceConstraintHandler

class TxnCollateralCreditFacility(AbstractCreditFacility):

    def __init__(self):
        super().__init__()
        self.collateralized_transactions = {}

    def calculate_fee(self, credit_amount) -> float:
        return 0.0
    
    def lend_credit(self, account: Account, amount: float) -> None:
        if amount > account.posted_collateral:
            # check if there are incoming transactions that can be used as collateral
            # use the incoming transaction with the lowest value that exceeds the amount being requested
            lowest_valid_amt = float('inf')
            lowest_valid_amt_txn = None
            for transaction in {txn for txn in account.txn_in if txn.status_code == 0 and txn not in self.collateralized_transactions.get(account.id, set())}:
                if transaction.amount >= amount and transaction.amount < lowest_valid_amt:
                    lowest_valid_amt = transaction.amount
                    lowest_valid_amt_txn = transaction
            if lowest_valid_amt_txn is not None:
                self.collateralized_transactions.setdefault(account.id, set()).add(lowest_valid_amt_txn)
                self.used_credit[account.id].append(amount)
                account.balance += amount
                account.posted_collateral -= amount
        else:
            # use normal collateral process
            self.used_credit[account.id].append(amount)
            account.balance += amount
            account.posted_collateral -= amount

    def collect_repayment(self, account: Account) -> None:
        # not important for now
        pass

if __name__ == "__main__":
    simulation_name = 'Collateralized Txn'
    banks = {'name': ['b1', 'b2', 'b3']}
    accounts = {'id': ['acc1', 'acc2', 'acc3'], 'owner': ['b1', 'b2', 'b3'], 'balance': [0, 0, 0], 'posted_collateral': [0, 0, 0]}
    transactions = {'sender_account': ['acc1', 'acc2', 'acc3'], 
                    'receipient_account': ['acc2', 'acc3', 'acc1'], 
                    'amount': [1, 1, 1], 
                    'time': ['08:00', '08:00', '08:00']}
    sim = BasicSim(simulation_name, banks=banks, accounts=accounts, transactions=transactions, constraint_handler=MinBalanceConstraintHandler(0), credit_facility=SimpleCollateralized())
    sim.run()