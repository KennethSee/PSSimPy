# PSSimPy: A Payment and Settlement Systems Simulator Python Library

## Table of Contents
1. [Introduction](#introduction)
2. [Usage](#usage)
   - [Quick Start](#quick-start)
   - [Stress Test](#stress-test)
   - [Agent-Based Modeling](#agent-based-modeling)
3. [Customization Guide](#customization-guide)
   - [Constraint Handler](#constraint-handler)
   - [Queue](#queue)
   - [Credit Facility](#credit-facility)
   - [Transaction Fee](#transaction-fee)
   - [Bank](#bank)
5. [Features and API Overview](#features-and-api-overview)
6. [Contributing](#contributing)
7. [License](#license)

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

## Customization Guide

This section details the classes that can be customized for a more tailored simulation.

### Constraint Handler

Transactions pass through a constraint handler before it is sent to a queue. The constraint handler can be configured to have custom constraints and handling logic. To implement a custom constraint handler, you will need to create a subclass that inherits the `AbstractConstraintHandler` class and implement the following abstract method in the subclass:

* `process_transaction(self, transaction)`: For a given transaction, if it passes the constraint check, it should be added to the `self.passed_transactions` list to indicate that it should be sent for further processing. If the transaction fails the constraint check, it should update the transaction status to "Failed".

The constraint handler can handle both hard and soft failures. Hard failure means that if the transaction fails to meet the constraint(s) defined, it will immediately be updated as a failed transaction. `MinBalanceContraintHandler` can be referred to as an example of a hard failure implementation. Soft failure means that if the transaction is unable to meet the constraint(s) defined, it can be modified and reran through the constraint handler until it complies with the constraint(s). `MaxSizeConstraintHandler` can be referred to as an example of a soft failure implementation. Both examples can be found in the constraint_handler folder in the code.

### Queue

This pertains to the transaction queue used in the simulation. To implement a custom queue, you will need to create a subclass that inherits the `AbstractQueue` class and implement the following abstract methods in the subclass:

* `sorting_logic(queue_item)`: This should be implemented to return an integer that represents the priority of the transaction to be inserted into the queue, where a lower integer represents a higher priority.
* `dequeue_criteria(queue_item)`: Defines conditions under which transactions are dequeued. Return True for transactions that meet the dequeue criteria. 

Note that `queue_item` is a tuple of a Transaction class and an integer representing the current period, where the higher the integer, the later the period in the simulation day.

Please refer to premade implementations (`DirectQueue`, `FIFOQueue`, `PriorityQueue`) within the queues folder in the code base for examples.

### Credit Facility

The `AbstractCreditFacility` class provides a framework for managing credit facilities, including lending credit, collecting repayments, and calculating fees. It is designed to be extended with custom logic specific to different credit systems. To create a custom credit facility, extend `AbstractCreditFacility` and implement the following abstract methods:

* `calculate_fee()`: Implement this method to define how the fee amount for credit is calculated. This method should return the fee amount as a float.
* `lend_credit(account, amount)`: Define the logic for lending credit to an account. This includes updating account balances and tracking lent amounts. This method does not return a value.
* `collect_repayment(account)`: Implement repayment collection for an account. This should adjust account balances and update the tracking of lent amounts and fees. This method does not return a value.

### Transaction Fee

Transaction fees are recorded for each processed transaction. `FixedTransactionFee` has been provided as a class that can be used to calculate the fee based on a fixed rate float value provided in the simulation parameters. However, if a dynamic transaction fee logic (e.g. different rates applied to transactions settled at different times in the day) is required, you will need to implement a subclass that inherits the `AbstractTransactionFee` class and implement the following abstract method in the subclass:

* `calculate_fee(self, txn_amount, time, rate)`: Calculates and returns the fee that should recorded for the given transaction amount. The rate argument can either be a float value or a dictionary with a string (to represent the effective time) as the key and a float (the rate associated with the respective key) as the value.

### Bank

The `Bank` class provides a basic implementation suitable for most use cases. However, in agent-based modeling, different banks may employ diverse strategies. This guide explains how to inherit from the Bank class to define custom strategies that banks might use in response to different simulation scenarios. To define a type of bank with a specific strategy, create a new class that extends `Bank`, allowing you to override and redefine the following method:

* `strategy(self, txns_to_settle, sim_name, day, current_time, queue)`: Implement this method to determine how for a given set of transactions that a bank needs to settle, which transactions it decides to proceed with settlement. The transactions to be sent for settlement should be returned as a set. Not all the parameters need to be utilized - they are provided to allow for the strategy to leverage a comprehensive set of information present in the simulation and can be used as needed.

Refer to the `PettyBank` class within the Agent-Based Modeling subsection above for an example of an implementation of a bank with a custom strategy.

## Features and API Overview

### `BasicSim` Class

The `BasicSim` class supports basic simulation functionalities for modeling payment and settlement systems. It is initialized by defining operational parameters and simulation entities such as banks, accounts, and transactions. Users can configure for bank failures to assess the impact on financial system stability. Each simulation run processes transactions daily within predefined operational hours and processing windows, utilizing a constraint, queue, credit facility, and transaction fee handlers. Additionally, the class records detailed transaction logs, capturing essential data and statistics for in-depth post-simulation analysis.

**Attributes**

| Attribute                 | Type                                                          | Description                                                                 |
|---------------------------|---------------------------------------------------------------|-----------------------------------------------------------------------------|
| `name`                    | `str`                                                         | The name of the simulation, used as a unique identifier.                    |
| `banks`                   | `Union[pd.DataFrame, Dict[str, List]]`                        | List of banks involved in the simulation.                                   |
| `accounts`                | `Union[pd.DataFrame, Dict[str, List]]`                        | List of accounts within the simulation.                                     |
| `transactions`            | `Union[pd.DataFrame, Dict[str, List]]`                        | List of transactions to be processed during the simulation.                 |
| `open_time`               | `str` (default: '08:00')                                      | The opening time for each simulation day, formatted as HH:MM.               |
| `close_time`              | `str` (default: '17:00')                                      | The closing time for each simulation day, formatted as HH:MM.               |
| `processing_window`       | `int` (default: 15)                                           | Duration in minutes of each processing window within a simulation day.      |
| `num_days`                | `int` (default: 1)                                            | The number of days the simulation runs.                                     |
| `constraint_handler`      | `AbstractConstraintHandler` (default: `PassThroughHandler()`) | A handler that processes transactions before they are queued.               |
| `queue`                   | `AbstractQueue` (default: `DirectQueue()`)                    | A queue system used to manage the order and processing of transactions.     |
| `credit_facility`         | `AbstractCreditFacility` (default: `SimplePriced()`)          | A mechanism for managing credit allocations and repayments.                 |
| `transaction_fee_handler` | `AbstractTransactionFee` (default: `FixedTransactionFee()`)   | A handler to calculate and apply transaction fees based on a given rate. |
| `transaction_fee_rate`    | `Union[float, Dict[str, float]]` (default: 0.0)               | The rate(s) at which transaction fees are calculated                        |
| `bank_failure`            | `Dict[int, List[Tuple[str, str]]]` (optional)                 | Days and times when particular banks are set to fail during the simulation. |
| `eod_clear_queue`         | `bool` (default: False)                                       | Option to cancel all transactions still in queue at EOD.                    |
| `eod_force_settlement`    | `bool` (default: False)                                       | Option to force all outstanding transactions in queue to settle at EOD.     |

**Methods**

| Method  | Parameters | Return Type | Description                                           |
|---------|------------|-------------|-------------------------------------------------------|
| `run()` | None       | None        | Runs the simulation for the specified number of days. |

### `ABMSim` Class

The `ABMSim` class is similar to the `BasicSim` class, but with a specific purpose to support agent-based simulation functionalities. Notably, it allows users to define custom bank strategies. This class allows users to either provide a list of transactions as input (the same way as `BasicSim`) or have the simulation generate the transactions randomly. The latter is achieved by omitting the `transactions` parameter and defining the `txn_arrival_prob`, `txn_amount_range` and `txn_priority_range` (optional) parameters.

**Attributes**

| Attribute                 | Type                                                          | Description                                                                 |
|---------------------------|---------------------------------------------------------------|-----------------------------------------------------------------------------|
| `name`                    | `str`                                                         | The name of the simulation, used as a unique identifier.                    |
| `banks`                   | `Union[pd.DataFrame, Dict[str, List]]`                        | List of banks involved in the simulation.                                   |
| `accounts`                | `Union[pd.DataFrame, Dict[str, List]]`                        | List of accounts within the simulation.                                     |
| `transactions`            | `Union[pd.DataFrame, Dict[str, List]]` (optional)             | List of transactions to be processed during the simulation.                 |
| `strategy_mapping`        | `dict`  (optional)                                            | The mapping of strategy types to their implemented classes.                 |
| `open_time`               | `str` (default: '08:00')                                      | The opening time for each simulation day, formatted as HH:MM.               |
| `close_time`              | `str` (default: '17:00')                                      | The closing time for each simulation day, formatted as HH:MM.               |
| `processing_window`       | `int` (default: 15)                                           | Duration in minutes of each processing window within a simulation day.      |
| `num_days`                | `int` (default: 1)                                            | The number of days the simulation runs.                                     |
| `constraint_handler`      | `AbstractConstraintHandler` (default: `PassThroughHandler()`) | A handler that processes transactions before they are queued.               |
| `queue`                   | `AbstractQueue` (default: `DirectQueue()`)                    | A queue system used to manage the order and processing of transactions.     |
| `credit_facility`         | `AbstractCreditFacility` (default: `SimplePriced()`)          | A mechanism for managing credit allocations and repayments.                 |
| `transaction_fee_handler` | `AbstractTransactionFee` (default: `FixedTransactionFee()`)   | A handler to calculate and apply transaction fees based on a given rate. |
| `transaction_fee_rate`    | `Union[float, Dict[str, float]]` (default: 0.0)               | The rate(s) at which transaction fees are calculated                        |
| `bank_failure`            | `Dict[int, List[Tuple[str, str]]]` (optional)                 | Days and times when particular banks are set to fail during the simulation. |
| `eod_clear_queue`         | `bool` (default: False)                                       | Option to cancel all transactions still in queue at EOD.                    |
| `eod_force_settlement`    | `bool` (default: False)                                       | Option to force all outstanding transactions inside and outside queue to settle at EOD.     |
| `txn_arrival_prob`        | `float` (optional)                                            | The probability that a transaction between two accounts occurs in a period. |
| `txn_amount_range`        | `Tuple[int, int]` (optional)                                  | The range of values a generated transaction could have.                     |
| `txn_priority_range`      | `Tuple[int, int]` (default: (1, 1))                           | The range of values a generated transaction's priority could have.          |

**Methods**

| Method  | Parameters | Return Type | Description                                           |
|---------|------------|-------------|-------------------------------------------------------|
| `run()` | None       | None        | Runs the simulation for the specified number of days. |

## Contributing
The main objective of this project is to democratize LVPS research. Anybody is welcome to submit code that could make our library more efficient and comprehensive. We especially welcome contributions of implemented abstract classes to be included as part of the library's offerings.

Contributors can make a Pull request for the development team to review proposed code changes. Individuals who are interested in becoming part of the core development team can email Kenneth at see.k@u.nus.edu.

## License
PSSimPy is made available under the MIT License, which provides a permissive free software license that allows for reuse within proprietary software provided all copies of the licensed software include a copy of the MIT License terms. This offers both flexibility and freedom to users and developers of PSSimPy.

For the full license text, please refer to the LICENSE file included in the distribution or visit https://opensource.org/licenses/MIT.
