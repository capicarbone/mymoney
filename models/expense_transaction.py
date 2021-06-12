
import mongoengine
from decimal import Decimal
from models.account_transaction import AccountTransaction
from models.statement import Statement
from models.transaction import Transaction
from models.fund import Fund
from utils import fund_utils
from mongoengine import signals

class ExpenseTransaction(Transaction):

    def __init__(self, **kwargs):

        parameters = self._extract_utilitaries_paramenters(kwargs)

        change: Decimal = parameters[0]
        account_id: str = parameters[1]

        super().__init__(**kwargs)

        if change and account_id:
            account_transaction = AccountTransaction(account=account_id, change=change)
            self.account_transactions.append(account_transaction)



    def clean(self):

        if not self.category or self.category.is_income():
            raise mongoengine.ValidationError("Expense transaction needs an expense category")

        if len(self.account_transactions) == 0:
            raise mongoengine.ValidationError('Change or account id missing')

        if self.account_transactions[0].change >= 0:
            raise mongoengine.ValidationError("Change must be negative")

    def __process_expense(self):

        fund = Fund.objects(categories=self.category, owner=self.owner).get()

        assignments = fund_utils.create_assignments_for_expense(fund, self.total_change)
        self.fund_transactions = assignments

    def adjust_change(self, change):

        super().adjust_change(change)

        if change >= 0:
            raise mongoengine.ValidationError("Change invalid.")

        new_account_transaction = self.account_transactions[0]
        new_account_transaction.change = Decimal(change).quantize(Decimal('1.00'))

        new_fund_transactions = fund_utils.create_assignments_for_expense(self.fund_transactions[0].fund.fetch(), self.total_change)

        # TODO: I should add adjustments for funds that are currently above their max limit and those removed fund above 0

        self.update(account_transactions=[new_account_transaction], fund_transactions=new_fund_transactions)

    @classmethod
    def pre_save_post_validation(cls, sender, document: 'ExpenseTransaction', created):
        document.__process_expense()

        assert sum([ft.change for ft in document.fund_transactions]) == document.total_change



signals.post_save.connect(Statement.transaction_post_save, sender=ExpenseTransaction)
signals.post_delete.connect(Statement.transaction_post_delete, sender=ExpenseTransaction)
signals.pre_save_post_validation.connect(ExpenseTransaction.pre_save_post_validation, sender=ExpenseTransaction)
