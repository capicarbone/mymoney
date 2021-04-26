
from copy import copy, deepcopy
from decimal import Decimal
import mongoengine
from flask_mongoengine import Document
import datetime
from .fund_transaction import FundTransaction
from models.account_transaction import AccountTransaction
from models.category import TransactionCategory
from models.user import User
from mongoengine import signals
from models.period_statement import PeriodStatement


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
        """
        :return: Transaction money change.
        """
        return sum([t.change for t in self.account_transactions])

    def is_transfer(self) -> bool:
        return self.total_change == 0

    def is_income(self) -> bool:
        return self.total_change > 0

    def is_expense(self) -> bool:
        return not self.is_income() and not self.is_transfer()

    def get_fund_transaction(self, fund) -> FundTransaction:
        return next((fund_transaction for fund_transaction in self.fund_transactions if fund == fund_transaction.fund),
                    None)

    def __neg__(self):
        """
        :return: Equivalent transaction for reverse it or object copy with values in inverse sign.
        """
        reverse_transaction = Transaction(owner=deepcopy(self.owner),
                                           description=deepcopy(self.description),
                                           date_accomplished=deepcopy(self.date_accomplished),
                                           created_at=deepcopy(self.created_at),
                                           category=deepcopy(self.category)
                                           )

        for acc_transacttion in self.account_transactions:
            rev_acc_transacction = AccountTransaction(account=acc_transacttion.account,
                                                      change=-acc_transacttion.change)
            reverse_transaction.account_transactions.insert(len(reverse_transaction.account_transactions),
                                                            rev_acc_transacction)

        for fnd_transaction in self.fund_transactions:
            rev_fund_transaction = FundTransaction(fund=fnd_transaction.fund,
                                                   change=-fnd_transaction.change)
            reverse_transaction.fund_transactions.insert(len(reverse_transaction.fund_transactions),
                                                         rev_fund_transaction)

        return reverse_transaction

signals.post_delete.connect(PeriodStatement.transaction_post_delete, sender=Transaction)