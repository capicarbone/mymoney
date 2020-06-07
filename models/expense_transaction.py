
import mongoengine
from decimal import Decimal
from models.account_transaction import AccountTransaction
from models.transaction import Transaction
from models.fund import Fund
from models.category import FundCategory
from utils import fund_utils
from mongoengine import signals

class ExpenseTransaction(Transaction):
    category = mongoengine.ReferenceField(FundCategory)

    def __init__(self, **kwargs):

        if not 'change' in kwargs or not 'account_id' in kwargs:
            mongoengine.ValidationError('Missing fields.')

        change: Decimal = kwargs.pop('change')
        account_id: str = kwargs.pop('account_id')

        if change >= 0:
            raise mongoengine.ValidationError("Change must be negative for an expense")

        super().__init__(**kwargs)

        account_transaction = AccountTransaction(account=account_id, change=change)
        self.account_transactions.append(account_transaction)

    def __process_expense(self):

        fund = Fund.objects(categories=self.category).get()

        assignments = fund_utils.create_assigments_for_expense(fund, self.total_change)
        self.fund_transactions = assignments

    @classmethod
    def pre_save_post_validation(cls, sender, document: 'ExpenseTransaction', created):
        document.__process_expense()

        assert sum([ft.change for ft in document.fund_transactions]) == document.total_change

signals.pre_save_post_validation.connect(ExpenseTransaction.pre_save_post_validation, sender=ExpenseTransaction)