from decimal import Decimal
import mongoengine
from flask_mongoengine import Document
import datetime

from .fund_transaction import FundTransaction

from models.account_transaction import AccountTransaction
from models.category import TransactionCategory
from models.user import User
from models.month_statement import MonthStatement, CategoryChange, AccountChange, FundChange


def validate_change(value: float):
    if value == 0:
        raise mongoengine.ValidationError()


class Transaction(Document):
    owner = mongoengine.LazyReferenceField(User, required=True)
    description = mongoengine.StringField(max_length=50)
    date_accomplished = mongoengine.DateTimeField(required=True)
    created_at = mongoengine.DateTimeField(default=lambda: datetime.datetime.now())
    account_transactions = mongoengine.EmbeddedDocumentListField(AccountTransaction)
    fund_transactions = mongoengine.EmbeddedDocumentListField(FundTransaction)
    category = mongoengine.ReferenceField(TransactionCategory)

    meta = {'allow_inheritance': True}

    def adjust_change(self, change):

        if self.is_transfer():
            raise mongoengine.ValidationError("Transaction is a transfer.")

    @property
    def total_change(self) -> Decimal:
        return sum([t.change for t in self.account_transactions])

    def is_transfer(self) -> bool:
        return self.total_change == 0

    def is_income(self) -> bool:
        return self.total_change > 0

    def get_fund_transaction(self, fund) -> FundTransaction:
        return next((fund_transaction for fund_transaction in self.fund_transactions if fund == fund_transaction.fund),
                    None)

    def _register_to_statement(self):

        if self.is_transfer():
            return

        try:
            month_statement = MonthStatement.objects(owner=self.owner,
                                                     month=self.date_accomplished.month,
                                                     year=self.date_accomplished.year).get()
        except mongoengine.DoesNotExist:
            month_statement = MonthStatement(owner=self.owner,
                                             month=self.date_accomplished.month,
                                             year=self.date_accomplished.year)

        category_change = month_statement.get_cateogry_change(self.category.id)

        if category_change is None:
            category_change = CategoryChange(category=self.category)
            month_statement.categories.insert(0, category_change)

        category_change.change += self.total_change

        account = self.account_transactions[0].account
        account_change = month_statement.get_account_change(account)

        if account_change is None:
            account_change = AccountChange(account=account)
            month_statement.accounts.insert(0, account_change)

        if self.total_change > 0:
            account_change.income += self.total_change
        else:
            account_change.expense += self.total_change

        for fund_transaction in self.fund_transactions:
            fund_change = month_statement.get_fund_change(fund_transaction.fund)

            if fund_change is None:
                fund_change = FundChange(fund=fund_transaction.fund)
                month_statement.funds.insert(0, fund_change)

            if fund_transaction.change > 0:
                fund_change.income += fund_transaction.change
            else:
                fund_change.expense += fund_transaction.change

        month_statement.last_transaction_processed = self.id
        month_statement.save()
