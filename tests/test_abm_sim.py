from PSSimPy.simulator import ABMSim
from PSSimPy.utils import minutes_between

banks = {'name': ['b1', 'b2'], 'random_facts': [123, 35234]}
accounts = {'id': ['acc1', 'acc2'], 'owner': ['b1', 'b2'], 'balance': [100, 100]}
transactions = {'sender_account': ['acc1', 'acc2'], 'receipient_account': ['acc2', 'acc1'], 'amount': [10, 5], 'time': ['08:15', '08:50']}
sim = ABMSim('Test ABM', banks, accounts, transactions, open_time='08:00', close_time='09:00')

sim.run()

print(sim.accounts['acc2'].balance)