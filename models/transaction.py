from typing import List
from decimal import Decimal
import mongoengine
from mongoengine import signals
from flask_mongoengine import Document
import datetime
from .fund import Fund
from .fund_transaction import FundTransaction
from utils import fund_utils
from .category import FundCategory
from models.account_transaction import AccountTransaction
from models.user import User
import pdb

def validate_change(value: float):
    if value == 0:
        raise mongoengine.ValidationError()




class Transaction(Document):
    owner = mongoengine.LazyReferenceField(User)
    description = mongoengine.StringField(max_length=50)
    time_accomplished = mongoengine.DateTimeField(required=True)
    created_at = mongoengine.DateTimeField(default=lambda: datetime.datetime.now())
    category = mongoengine.ReferenceField(FundCategory)
    account_transactions = mongoengine.EmbeddedDocumentListField(AccountTransaction)
    fund_transactions = mongoengine.EmbeddedDocumentListField(FundTransaction)

    @classmethod
    def create_income(cls, account_id: str, change: Decimal, description: str, time_accomplished: datetime, owner: User):

        if change <= 0:
            raise mongoengine.ValidationError("Change must be positive for an income")

        new_transaction = Transaction(description=description, time_accomplished=time_accomplished, owner=owner)
        account_transaction = AccountTransaction(account=account_id, change=change)
        new_transaction.account_transactions.append(account_transaction)

        return new_transaction


    @classmethod
    def create_expense(cls, account_id: str, change: Decimal, description: str, time_accomplished: datetime,
                       category_id: str, owner: User):

        if change >= 0:
            raise mongoengine.ValidationError("Change must be negative for an outcome")

        new_transaction = Transaction(description=description, category=category_id, time_accomplished=time_accomplished, owner=owner)
        account_transaction = AccountTransaction(account=account_id, change=change)
        new_transaction.account_transactions.append(account_transaction)

        return new_transaction

    @classmethod
    def create_account_transfer(cls, owner:User, from_account_id:str, to_account_id:str, amount:Decimal, description:str, time_accomplished:datetime ):
        if amount == 0:
            raise mongoengine.ValidationError("Amount must be different than zero")

        new_transaction = Transaction(owner=owner, description=description, time_accomplished=time_accomplished)
        from_account_transaction = AccountTransaction(account=from_account_id, change=-amount)
        to_account_transaction = AccountTransaction(account=to_account_id, change=amount)
        new_transaction.account_transactions.append(from_account_transaction)
        new_transaction.account_transactions.append(to_account_transaction)

        return new_transaction

    def adjust_change(self, change):

        if self.is_transfer():
            raise mongoengine.ValidationError("Transaction is a transfer.")

        if change > 0 and not self.is_income():
            raise mongoengine.ValidationError("Change invalid.")

        for account_transaction in self.account_transactions:
            account_transaction.change = change

        new_fund_transactions : List[FundTransaction] = []
        if self.is_income():

            funds_to_adjust = Fund.objects(owner=self.owner, is_active=True)

            new_fund_transactions = fund_utils.create_assignments_for_income(funds_to_adjust, change, self.time_accomplished, self.id)

        else:
            new_fund_transactions = fund_utils.create_assigments_for_expense(self.fund_transactions[0].fund.get(), change)

        new_account_transaction = self.account_transactions[0]
        new_account_transaction.change = change

        # TODO: I should add adjustments for funds that are currently above their max limit and those removed fund above 0

        self.update(account_transactions=[new_account_transaction], fund_transactions=new_fund_transactions)




    @property
    def total_change(self) -> Decimal:
        return sum([t.change for t in self.account_transactions])

    def is_transfer(self) -> bool:
        return self.total_change == 0

    def is_income(self) -> bool:
        return self.total_change > 0

    def get_fund_transaction(self, fund) -> FundTransaction:
        return next((fund_transaction for fund_transaction in self.fund_transactions if fund == fund_transaction.fund), None)

    def __proccess_income(self):

        funds = Fund.objects().actives_for(self.owner)
        assignments = fund_utils.create_assignments_for_income(funds, self.total_change, self.time_accomplished)
        self.fund_transactions = assignments


    def __process_expense(self):

        fund = Fund.objects(categories=self.category).get()

        assignments = fund_utils.create_assigments_for_expense(fund, self.total_change)
        self.fund_transactions = assignments


    @classmethod
    def pre_save_post_validation(cls, sender, document: 'Transaction', created):

        if not document.is_transfer():
            if  document.is_income():
                document.__proccess_income()
            else:
                document.__process_expense()

            #assert 0.99 <= sum([ft.assigment for ft in document.fund_transactions]) <= 1 # for the moment a margin of 0.01 es accepted
            assert sum([ft.change for ft in document.fund_transactions]) == document.total_change


signals.pre_save_post_validation.connect(Transaction.pre_save_post_validation, sender=Transaction)
