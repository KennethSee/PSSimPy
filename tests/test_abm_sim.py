from PSSimPy.simulator import ABMSim
from PSSimPy.utils import minutes_between
from PSSimPy import Bank
import pandas as pd

# banks = {'name': ['b1', 'b2', 'b3'], 'random_facts': [123, 35234, 31]}
# accounts = {'id': ['acc1', 'acc2', 'acc3'], 'owner': ['b1', 'b2', 'b3'], 'balance': [100, 100, 100]}
# transactions = {'sender_account': ['acc1', 'acc2'], 'receipient_account': ['acc2', 'acc1'], 'amount': [10, 5], 'time': ['08:15', '08:50']}
# bank_failure = {1: [('08:30', 'b1')]}

# sim = ABMSim('Test ABM', banks, accounts, transactions, open_time='08:00', close_time='09:00', transaction_fee_rate=0.01, bank_failure=bank_failure)
# sim.run()

# print(sim.accounts['acc1'].balance)
# print(sim._account_mappings())


# banks = {'name': ['b1', 'b2', 'b3']}
# accounts = {'id': ['acc1', 'acc2', 'acc3'], 'owner': ['b1', 'b2', 'b3'], 'balance': [100, 100, 100]}
# sim = ABMSim('Test rand txn arrival', banks, accounts, num_days=2, open_time='08:00', close_time='09:00', txn_arrival_prob=0.5, txn_amount_range=(1, 100))
# sim.run()
# print(sim.accounts['acc1'].balance, sim.accounts['acc2'].balance, sim.accounts['acc3'].balance)
class PettyBank(Bank):
    """This class of banks will not settle transactions to another bank's account if the counter party has an outstanding transaction to this bank that is not yet settled."""

    def __init__(self, name, strategy_type='Petty', **kwargs):
        super().__init__(name, strategy_type, **kwargs)
    
    # overwrite strategy
    def strategy(self, txns_to_settle: set, all_outstanding_transactions: set, sim_name: str, day: int, current_time: str, queue) -> set:
        # identify the counterparty bank of outstanding transactions where this bank is the recipient bank
        counterparties_with_outstanding = {transaction.sender_account.owner.name for transaction in all_outstanding_transactions if transaction.receipient_account.owner.name == self.name}
        # exclude transactions which involve paying the identified counterparties
        chosen_txns_to_settle = {transaction for transaction in txns_to_settle if transaction.receipient_account.owner.name not in counterparties_with_outstanding}
        return chosen_txns_to_settle


banks = {'name': ['b1', 'b2', 'b3', 'b4'], 'strategy_type': ['Petty', 'Petty', 'Petty', 'Petty']}
accounts = {'id': ['acc1', 'acc2', 'acc3', 'acc4'], 'owner': ['b1', 'b2', 'b3', 'b4'], 'balance': [100, 100, 100, 100]}
transactions = {'sender_account': ['acc1', 'acc2', 'acc3', 'acc4'], 'receipient_account': ['acc2', 'acc3', 'acc4', 'acc1'], 'amount': [10, 10, 10, 10], 'time': ['08:30', '08:30', '08:30', '08:30']}

sim = ABMSim('Petty ABM', banks=banks, accounts=accounts, transactions=transactions, strategy_mapping= {'Petty': PettyBank}, open_time='08:00', close_time='09:00', processing_window=30)
sim.run()