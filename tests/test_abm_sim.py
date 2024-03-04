from PSSimPy.simulator import ABMSim
from PSSimPy.utils import minutes_between

banks = {'name': ['b1', 'b2'], 'random_facts': [123, 35234]}
accounts = {'id': ['acc1', 'acc2'], 'owner': ['b1', 'b2']}
sim = ABMSim('Test ABM', banks, accounts)

print(sim.banks['b1'].random_facts)