
import mongoengine

from models.fund_transaction import FundTransaction
from models.transaction import Transaction


class FundTransferTransaction(Transaction):

    def __init__(self, **kwargs):
        amount = kwargs.pop('amount')
        to_fund_id = kwargs.pop('to_fund_id')
        from_fund_id = kwargs.pop('from_fund_id')
        super().__init__(**kwargs)

        if to_fund_id and from_fund_id and amount:

            if amount == 0:
                raise mongoengine.ValidationError("Amount must be different than zero")

            from_fund_transaction = FundTransaction(fund=from_fund_id, change=-amount)
            to_fund_transaction = FundTransaction(fund=to_fund_id, change=amount)
            self.fund_transactions.append(from_fund_transaction)
            self.fund_transactions.append(to_fund_transaction)