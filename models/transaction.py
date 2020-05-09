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



    @classmethod
    def pre_save_post_validation(cls, sender, document, created):

        funds = Fund.objects().actives_for(document.owner)

        for fund in funds:

            change = document.change * fund.percentage_assigment

            #print(cls.objects(owner=document.owner, fund_transactions__fund=fund)._query)
            try:
                last_transaction = cls.objects(owner=document.owner, fund_transactions__fund=fund).order_by('-time_accomplished', '-created_at')[0]
            except IndexError:
                last_transaction = None

            if last_transaction:
                fund_transaction = last_transaction.get_fund_transaction(fund)
                balance = fund_transaction.current_balance + change
            else:
                balance = change

            f_transaction = FundTransaction(current_balance=balance, change=change, fund=fund)
            document.fund_transactions.append(f_transaction)


signals.pre_save_post_validation.connect(AccountTransaction.pre_save_post_validation, sender=AccountTransaction)
