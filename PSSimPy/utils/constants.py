TRANSACTION_STATUS_CODES = {'Open': 0, 'Modified': 1, 'Success': 2, 'Failed': -1}

TRANSACTION_LOGGER_HEADER = ('day', 'time', 'from_account', 'to_account', 'amount', 'status')
TRANSACTION_FEE_LOGGER_HEADER = ('account', 'day', 'time', 'fee')
QUEUE_STATS_HEADER = ('day', 'time', 'num_txns_in_queue', 'txn_amount_in_queue')
TRANSACTION_ARRIVAL_HEADER = ('day', 'time', 'from_account', 'to_account', 'amount', 'priority')
ACCOUNT_BALANCE_HEADER = ('day', 'time', 'account', 'balance')
CREDIT_FACILITY_LOGGER_HEADER = ('day', 'time', 'account', 'posted_collateral', 'total_credit', 'total_fee')