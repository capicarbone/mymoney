
import mongoengine
from decimal import Decimal
from models.account_transaction import AccountTransaction
from models.transaction import Transaction
from models.fund import Fund
from utils import fund_utils
from mongoengine import signals

class IncomeTransaction(Transaction):

    def __init__(self, **kwargs):

        if not 'change' in kwargs or not 'account_id' in kwargs:
            raise mongoengine.ValidationError('Missing fields.')

        change:Decimal = kwargs.pop('change')
        account_id:str = kwargs.pop('account_id')

        if change <= 0:
            raise mongoengine.ValidationError("Change must be positive for an income")

        super().__init__(**kwargs)

        account_transaction = AccountTransaction(account=account_id, change=change)
        self.account_transactions.append(account_transaction)

    def __proccess_income(self):

        funds = Fund.objects().actives_for(self.owner)
        assignments = fund_utils.create_assignments_for_income(funds, self.total_change, self.time_accomplished)
        self.fund_transactions = assignments

    @classmethod
    def pre_save_post_validation(cls, sender, document: 'IncomeTransaction', created):
        document.__proccess_income()

        assert sum([ft.change for ft in document.fund_transactions]) == document.total_change


signals.pre_save_post_validation.connect(IncomeTransaction.pre_save_post_validation, sender=IncomeTransaction)



