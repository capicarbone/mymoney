
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

        change: Decimal = kwargs.pop('change') if 'change' in kwargs else None
        account_id: str = kwargs.pop('account_id') if 'account_id' in kwargs else None

        super().__init__(**kwargs)

        if change and account_id:
            account_transaction = AccountTransaction(account=account_id, change=change)
            self.account_transactions.append(account_transaction)

    def clean(self):
        if not self.category:
            raise mongoengine.ValidationError("Expense transaction needs an expense category")

    def __process_expense(self):

        fund = Fund.objects(categories=self.category).get()

        assignments = fund_utils.create_assigments_for_expense(fund, self.total_change)
        self.fund_transactions = assignments

    def adjust_change(self, change):

        super().adjust_change(change)

        if change >= 0:
            raise mongoengine.ValidationError("Change invalid.")

        new_fund_transactions = fund_utils.create_assigments_for_expense(self.fund_transactions[0].fund.fetch(), change)

        new_account_transaction = self.account_transactions[0]
        new_account_transaction.change = change

        # TODO: I should add adjustments for funds that are currently above their max limit and those removed fund above 0

        self.update(account_transactions=[new_account_transaction], fund_transactions=new_fund_transactions)

    @classmethod
    def pre_save_post_validation(cls, sender, document: 'ExpenseTransaction', created):
        document.__process_expense()

        assert sum([ft.change for ft in document.fund_transactions]) == document.total_change

signals.pre_save_post_validation.connect(ExpenseTransaction.pre_save_post_validation, sender=ExpenseTransaction)