# PSSimPy: A Payment and Settlement Systems Simulator Python Library

## Getting Started
```bash
pip install PSSimPy
```

## Usage

```python
from PSSimPy.simulator import BasicSim
from PSSimPy.constraint_handler import MinBalanceConstraintHandler
from PSSimPy.queues import FIFOQueue
from PSSimPy.credit_facilities import SimplePriced
from PSSimPy.transaction_fee import FixedTransactionFee

# initialize simulator
sim = BasicSims(name='my_lvps_sim', banks=banks, accounts=accounts, transactions=transactions, num_days=1, open_time='08:00', close_time='17:00', \
txn_arrival_prob=0.5, txn_amount_range=(1, 100), constraint_handler=MinBalanceConstraintHandler(), queue=FIFOQueue(), credit_facility=SimplePriced(), \
transaction_fee_handler=FixedTransactionFee())
# execute simulation
sim.run()
```
