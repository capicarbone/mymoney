import mongoengine
from mongoengine import signals
from flask_mongoengine import Document
import datetime
from .account import Account
from .fund import Fund
from .category import FundCategory
from models.fund_transaction import FundTransaction
from models.user import User


def validate_change(value: float):
    if value == 0:
        raise mongoengine.ValidationError()




class AccountTransaction(Document):
    owner = mongoengine.ReferenceField(User)
    description = mongoengine.StringField(max_length=50)
    account = mongoengine.ReferenceField(Account, required=True)
    time_accomplished = mongoengine.DateTimeField(required=True)
    change = mongoengine.FloatField(required=True, validation=validate_change)
    created_at = mongoengine.DateTimeField(default=lambda: datetime.datetime.now())
    category = mongoengine.ReferenceField(FundCategory)
    fund_transactions = mongoengine.EmbeddedDocumentListField(FundTransaction)

    def is_income(self) -> bool:
        return self.change > 0

    def get_fund_transaction(self, fund) -> FundTransaction:
        return next((fund_transaction for fund_transaction in self.fund_transactions if fund == fund_transaction.fund), None)

    def __proccess_income(self):

        funds = Fund.objects().actives_for(self.owner)

        for fund in funds:

            change = self.change * fund.percentage_assigment

            last_transaction = self.last_transaction_for(fund)

            if last_transaction:
                fund_transaction = last_transaction.get_fund_transaction(fund)
                balance = fund_transaction.current_balance + change
            else:
                balance = change

            f_transaction = FundTransaction(current_balance=balance, change=change, fund=fund)
            self.fund_transactions.append(f_transaction)

    def __process_expense(self):

        fund = Fund.objects(categories=self.category).get()
        last_transaction = self.last_transaction_for(fund).get_fund_transaction(fund)

        print("last transaction balance " + str(last_transaction.current_balance))

        if last_transaction.current_balance + self.change < 0:
            raise mongoengine.ValidationError('Insufficient funds')

        new_fund_transaction = FundTransaction(current_balance=last_transaction.current_balance + self.change,
                                               change=self.change,
                                               fund=fund)

        self.fund_transactions.append(new_fund_transaction)

    @classmethod
    def pre_save_post_validation(cls, sender, document: 'AccountTransaction', created):
        if document.is_income():
            document.__proccess_income()
        else:
            document.__process_expense()

    @classmethod
    def last_transaction_for(cls, fund: Fund) -> 'AccountTransaction':
        try:
            return AccountTransaction.objects(owner=fund.owner, fund_transactions__fund=fund) \
                .order_by('-time_accomplished', '-created_at')[0]
        except IndexError:
            return None

signals.pre_save_post_validation.connect(AccountTransaction.pre_save_post_validation, sender=AccountTransaction)
