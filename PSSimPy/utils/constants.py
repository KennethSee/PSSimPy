TRANSACTION_STATUS_CODES = {'Open': 0, 'Modified': 1, 'Success': 2, 'Failed': -1}

TRANSACTION_LOGGER_HEADER = ('day', 'time', 'from_account', 'to_account', 'amount', 'status')
TRANSACTION_FEE_LOGGER_HEADER = ('account', 'day', 'time', 'fee')