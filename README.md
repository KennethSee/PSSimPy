# PSSimPy: A Payment and Settlement Systems Simulator Python Library

# Table of Contents
1. [Introduction](#introduction)
2. [Usage](#usage)
   - [Quick Start](#quick-start)
   - [Stress Test](#stress-test)
   - [Agent-Based Modeling](#agent-based-modeling)
4. [Features and API Overview](#features-and-api-overview)
5. [Contributing](#contributing)

## Introduction

## Getting Started
```bash
pip install PSSimPy
```

## Usage
### Quick Start
```python
from PSSimPy.simulator import BasicSim
from PSSimPy.constraint_handler import MinBalanceConstraintHandler
from PSSimPy.queues import FIFOQueue
from PSSimPy.credit_facilities import SimplePriced
from PSSimPy.transaction_fee import FixedTransactionFee

# initialize simulator
sim = BasicSim(name='my_lvps_sim', banks=banks, accounts=accounts, transactions=transactions, num_days=1, open_time='08:00', close_time='17:00', \
txn_arrival_prob=0.5, txn_amount_range=(1, 100), constraint_handler=MinBalanceConstraintHandler(), queue=FIFOQueue(), credit_facility=SimplePriced(), \
transaction_fee_handler=FixedTransactionFee())
# execute simulation
sim.run()
```
### Stress Test

### Agent-Based Modeling

## Features and API Overview

## Contributing
The main objective of this project is to democratize LVPS research. Anybody is welcome to submit code that could make our library more efficient and comprehensive. We especially welcome contributions of implemented abstract classes to be included as part of the library's offerings.

Contributors can make a Pull request for the development team to review proposed code changes. Individuals who are interested in becoming part of the core development team can email Kenneth at see.k@u.nus.edu.
