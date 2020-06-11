
import mongoengine

from models.account_transaction import AccountTransaction
from models.transaction import Transaction


class AccountsTransferTransaction(Transaction):

    def __init__(self, **kwargs):

        amount = kwargs.pop('amount') if 'amount' in kwargs else None
        to_account_id = kwargs.pop('to_account_id') if 'to_account_id' in kwargs else None
        from_account_id = kwargs.pop('from_account_id') if 'from_account_id' in kwargs else None

        super().__init__(**kwargs)

        if amount and to_account_id and from_account_id:

            if amount == 0:
                raise mongoengine.ValidationError("Amount must be different than zero")


            from_account_transaction = AccountTransaction(account=from_account_id, change=-amount)
            to_account_transaction = AccountTransaction(account=to_account_id, change=amount)
            self.account_transactions.append(from_account_transaction)
            self.account_transactions.append(to_account_transaction)