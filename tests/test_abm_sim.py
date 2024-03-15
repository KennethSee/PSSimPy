from PSSimPy.simulator import ABMSim
from PSSimPy.utils import minutes_between
import pandas as pd

banks = {'name': ['b1', 'b2', 'b3'], 'random_facts': [123, 35234, 31]}
accounts = {'id': ['acc1', 'acc2', 'acc3'], 'owner': ['b1', 'b2', 'b3'], 'balance': [100, 100, 100]}
transactions = {'sender_account': ['acc1', 'acc2'], 'receipient_account': ['acc2', 'acc1'], 'amount': [10, 5], 'time': ['08:15', '08:50']}
bank_failure = {1: [('08:30', 'b1')]}

sim = ABMSim('Test ABM', banks, accounts, transactions, open_time='08:00', close_time='09:00', transaction_fee_rate=0.01, bank_failure=bank_failure)
sim.run()

print(sim.accounts['acc1'].balance)
# print(sim._account_mappings())
