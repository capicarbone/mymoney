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
