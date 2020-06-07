
import mongoengine

from models.account_transaction import AccountTransaction
from models.transaction import Transaction


class AccountsTransferTransaction(Transaction):

    def __init__(self, **kwargs):

        if not 'amount' in kwargs or not 'to_account_id' in kwargs or not 'from_account_id' in kwargs :
            raise mongoengine.ValidationError("Missing parameters")

        amount = kwargs.pop('amount')
        to_account_id = kwargs.pop('to_account_id')
        from_account_id = kwargs.pop('from_account_id')

        if amount == 0:
            raise mongoengine.ValidationError("Amount must be different than zero")

        super().__init__(**kwargs)
        from_account_transaction = AccountTransaction(account=from_account_id, change=-amount)
        to_account_transaction = AccountTransaction(account=to_account_id, change=amount)
        self.account_transactions.append(from_account_transaction)
        self.account_transactions.append(to_account_transaction)