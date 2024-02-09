# PSSimPy: A Payment and Settlement Systems Simulator Python Library

## Getting Started
```bash
pip install PSSimPy
```

## Usage

```python
from PSSimPy import BasicSim
from PSSimPy.settlement_mechanisms import SimpleRTGS
from PSSimPy.queues import DirectQueue
from PSSimPy.credit_facilities import SimplePriced

# initialize simulator
sim = BasicSim(open_time, close_time, num_days, settlement_mechanism=SimpleRTGS, queue=DirectQueue, credit_facility=SimplePriced)
# load accounts
# accounts_dict is a nested dictionary where the keys are the account IDs. Within the values of each account ID is a dictionary that has at least the following keys: owner, begin_balance.
sim.load_accounts(accounts_dict)
# load transactions
# txn_lst is a list of transactions where each element is a dictionary. The dictionary needs to have at least the following keys: sender_account, receipient_account, amount
sim.load_txn(txn_lst)
# execute simulation
sim.run_simulation()

# retrieve simulation results
sim.get_executed_txn_details()
sim.get_account_balance_history()
```