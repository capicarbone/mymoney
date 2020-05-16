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


class Transaction(Document):
    owner = mongoengine.LazyReferenceField(User)
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

            f_transaction = FundTransaction(change=change,
                                            assigment=fund.percentage_assigment,
                                            fund=fund)
            self.fund_transactions.append(f_transaction)

    def __process_expense(self):

        fund = Fund.objects(categories=self.category).get()

        # TODO: Validate enough balance

        new_fund_transaction = FundTransaction(change=self.change,
                                               assigment=1,
                                               fund=fund)

        self.fund_transactions.append(new_fund_transaction)


    @classmethod
    def pre_save_post_validation(cls, sender, document: 'Transaction', created):
        if document.is_income():
            document.__proccess_income()
        else:
            document.__process_expense()



signals.pre_save_post_validation.connect(Transaction.pre_save_post_validation, sender=Transaction)
