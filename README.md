# PSSimPy: A Payment and Settlement Systems Simulator Python Library

## Table of Contents
1. [Introduction](#introduction)
2. [Usage](#usage)
   - [Quick Start](#quick-start)
   - [Stress Test](#stress-test)
   - [Agent-Based Modeling](#agent-based-modeling)
4. [Features and API Overview](#features-and-api-overview)
5. [Contributing](#contributing)
6. [License](#license)

## Introduction
PSSimPy is a Python library designed to simulate Large Value Payment Systems (LVPS). This library serves as an advanced simulation tool that facilitates analysis of synthetic or real LVPS transaction data to test potential modifications and assess impacts on LVPS performance. 

This library is built with the flexibility to accommodate a wide range of simulation needs, catering to both academic researchers and industry/government analysts. Its modular architecture enables users to customize simulations to explore the intricacies of payment and settlement processes. This is a publicly available tool and we welcome any form of collaboration and feedback.

## Getting Started
```bash
pip install PSSimPy
```

## Usage
### Quick Start
First, import the simulator class.
```python
from PSSimPy.simulator import BasicSim
```
Define the banks, accounts, and transactions. They are defined as dictionaries here, but they can be Pandas dataframes as well.
```python
banks = {'name': ['b1', 'b2', 'b3']}
accounts = {'id': ['acc1', 'acc2', 'acc3'], 'owner': ['b1', 'b2', 'b3'], 'balance': [100, 100, 100], 'posted_collateral': [0, 0, 0]}
transactions = {'sender_account': ['acc1', 'acc2', 'acc3'], 
                 'recipient_account': ['acc2', 'acc3', 'acc1'], 
                 'amount': [1, 1, 1], 
                 'time': ['08:00', '08:10', '08:30']}
```
Initialize and run the simulator with the default settings. The name will be your simulation's unique identifier.
```python
sim = BasicSim(name='my_first_lvps_sim', banks=banks, accounts=accounts, transactions=transactions)
sim.run()
```
The simulation outputs can be retrieved from the CSV files generated in the same folder where you run your Python code.
### Stress Test
Bank failures can be incorporated into the model to observe the dynamics of the system when one or more bank fails at specific points in the scenario. To specify bank failure(s), define a dictionary to capture when the relevant bank fails. The dictionary's key should be the day of the failure and the values would be a list of tuples specifying the exact failure time and affected bank name. This dictionary should then be included as one of the parameters in the simulator's parameters.

```python
BANK_FAILURE =  {1:[('08:15', 'b1'), ('13:00', 'b2')]} # defining that on day 1, bank "b1" fails at 08:15 and bank "b2" fails at 13:00
stress_sim = BasicSim(..., bank_failure=BANK_FAILURE)
```

### Agent-Based Modeling
Agent-based models are supported by modeling Banks as strategic agents. Users can inherit the Bank class and overwrite the _strategy_ function to define a new strategy. Here, we create _PettyBank_ as an example of a strategic bank that will not make outgoing payments to a counterparty bank that owes it money.
```python
from PSSimPy import Bank

class PettyBank(Bank):
    """This class of banks will not settle transactions to another bank's account if the counter party has an outstanding transaction to this bank that is not yet settled."""

    def __init__(self, name, strategy_type='Petty', **kwargs):
        super().__init__(name, strategy_type, **kwargs)
    
    # overwrite strategy
    # note that the parameters defined here are inherited from the Bank class' strategy function
    # not all the parameters may be used but they have been included to allow strategies to access a comprehensive set of information
    def strategy(self, txns_to_settle: set, all_outstanding_transactions: set, sim_name: str, day: int, current_time: str, queue) -> set:
        # identify the counterparty bank of outstanding transactions where this bank is the recipient bank
        counterparties_with_outstanding = {transaction.sender_account.owner.name for transaction in all_outstanding_transactions if transaction.recipient_account.owner.name == self.name}
        # exclude transactions which involves paying the identified counterparties
        chosen_txns_to_settle = {transaction for transaction in txns_to_settle if transaction.recipient_account.owner.name not in counterparties_with_outstanding}
        return chosen_txns_to_settle
```
The agent-based simulation can then be conducted by fitting and running the ABMSim simulator class. Note the presence of the "strategy_mapping" argument. This should be a dictionary of strategy types to customized child Bank classes. This dictionary will then be used to map each bank's defined strategy type to the type of Bank class they should be initialized as.
```python
from PSSimPy.simulator import ABMSim

# redefine the banks variable to specify each bank's strategy type
# no change required to the accounts and transactions variables
banks = {'name': ['b1', 'b2', 'b3'], 'strategy_type': ['Petty', 'Petty', 'Petty']}

simulator_name = 'Petty ABM'
abm_sim = ABMSim(simulator_name, banks=banks, accounts=accounts, transactions=transactions, strategy_mapping={'Petty': PettyBank})
abm_sim.run()
```
ABMSim also supports endogenously generated transactions. To utilize this feature, the "transactions" argument can be omitted and be replaced by the "txn_arrival_prob" and "txn_amount_range" arguments. "txn_arrival_prob" should be a floating number between 0 and 1 to indicate the probability of a transaction being generated at each time period between two accounts owned by different banks. "txn_amount_range" should be a tuple of the minimum and maximum values of each transaction amount. The simulator will randomly generate a transaction value within the defined range for each generated transaction.
```python
abm_sim = ABMSim(name='Generated Transactions', banks=banks, accounts=accounts, txn_arrival_prob=0.5, txn_amount_range=(1, 100))
# execute simulation
abm_sim.run()
```

## Features and API Overview

## Contributing
The main objective of this project is to democratize LVPS research. Anybody is welcome to submit code that could make our library more efficient and comprehensive. We especially welcome contributions of implemented abstract classes to be included as part of the library's offerings.

Contributors can make a Pull request for the development team to review proposed code changes. Individuals who are interested in becoming part of the core development team can email Kenneth at see.k@u.nus.edu.

## License
PSSimPy is made available under the MIT License, which provides a permissive free software license that allows for reuse within proprietary software provided all copies of the licensed software include a copy of the MIT License terms. This offers both flexibility and freedom to users and developers of PSSimPy.

For the full license text, please refer to the LICENSE file included in the distribution or visit https://opensource.org/licenses/MIT.
