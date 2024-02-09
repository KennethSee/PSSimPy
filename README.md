# PSSimPy
Payment and Settlement Systems Simulator Python Library

## Get Startd
```bash
pip install PSSimPy
```

## Usage

```python
from PSSimPy import BasicSim

# initialize simulator
sim = BasicSim(open_time, close_time, num_days, settlement_mechanism='simple_RTGS', queue='direct', credit_facility='simple_priced')
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