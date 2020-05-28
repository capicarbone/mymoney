from decimal import Decimal
import mongoengine
from mongoengine import signals
from flask_mongoengine import Document
import datetime
from .account import Account
from .fund import Fund
from .category import FundCategory
from models.fund_transaction import FundTransaction
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
    def create_income(cls, accountId: str, change: Decimal, description: str, time_accomplished: datetime, owner: User):

        if change <= 0:
            raise mongoengine.ValidationError("Change must be positive for an income")

        new_transaction = Transaction(description=description, time_accomplished=time_accomplished, owner=owner)
        account_transaction = AccountTransaction(account=accountId, change=change)
        new_transaction.account_transactions.append(account_transaction)

        return new_transaction


    @classmethod
    def create_expense(cls, accountId: str, change: Decimal, description: str, time_accomplished: datetime,
                       categoryId: str,
                        owner: User):

        if change >= 0:
            raise mongoengine.ValidationError("Change must be negative for an outcome")

        new_transaction = Transaction(description=description, category=categoryId, time_accomplished=time_accomplished, owner=owner)
        account_transaction = AccountTransaction(account=accountId, change=change)
        new_transaction.account_transactions.append(account_transaction)

        return new_transaction

    @property
    def total_change(self) -> Decimal:
        return sum([t.change for t in self.account_transactions])

    def is_income(self) -> bool:
        return self.total_change > 0

    def get_fund_transaction(self, fund) -> FundTransaction:
        return next((fund_transaction for fund_transaction in self.fund_transactions if fund == fund_transaction.fund), None)

    def __proccess_income(self):

        funds = Fund.objects().actives_for(self.owner)
        default_fund: Fund = next((fund for fund in funds if fund.is_default))
        remaining = self.total_change
        total_adjustment = Decimal(0)

        funds_in_deficit = [fund for fund in funds if fund.get_deficit() > 0]

        total_deficit = sum([fund.get_deficit() for fund in funds_in_deficit])

        # Making assigment on funds with deficit, must be the priority
        for fund in funds_in_deficit:

            to_assign: Decimal = Decimal(self.total_change * fund.percentage_assigment)

            if total_deficit > self.total_change:
                to_assign = (self.total_change / len(funds_in_deficit)).quantize(Decimal('1.00'))
            else:
                if to_assign < fund.get_deficit():
                    adjustment = fund.get_deficit() - to_assign
                    to_assign = to_assign + adjustment
                    total_adjustment = total_adjustment + adjustment
                else:
                    if fund.maximum_limit and to_assign + fund.get_balance() > fund.maximum_limit:
                        to_assign = to_assign - ((to_assign + fund.get_balance()) - fund.maximum_limit)

            to_assign = to_assign if to_assign <= remaining else remaining

            fund_transaction = FundTransaction(change=to_assign,
                                               assigment=to_assign / self.total_change,
                                               fund=fund)
            self.fund_transactions.append(fund_transaction)

            remaining = remaining - to_assign


        assert 0 <= remaining <= self.total_change

        # Taking funds that does not have assigment yet
        funds_for_assignment = [fund for fund in funds if not next((t for t in self.fund_transactions if t.fund == fund and not fund.is_default),None)]


        if remaining > 0:
            adjustment = total_adjustment / len(funds_for_assignment)
            for fund in funds_for_assignment:

                if fund.maximum_limit is not None and fund.get_balance() >= fund.maximum_limit:
                    continue

                to_assign = (self.total_change * fund.percentage_assigment) - adjustment

                if to_assign < 0.009:
                    continue

                to_assign = to_assign if to_assign <= remaining else remaining

                f_transaction = FundTransaction(change=to_assign,
                                                assigment=to_assign / self.total_change,
                                                fund=fund)
                self.fund_transactions.append(f_transaction)
                remaining = remaining - to_assign

        assert 0 <= remaining < self.total_change

        if remaining > 0:
            to_assign = self.total_change - sum([ft.change for ft in self.fund_transactions])
            fund_transaction = FundTransaction(change=to_assign,
                                               assigment=to_assign / self.total_change,
                                               fund=default_fund)
            self.fund_transactions.append(fund_transaction)

    def __process_expense(self):

        fund = Fund.objects(categories=self.category).get()

        if fund.get_balance() - self.total_change.copy_abs() < 0:
            raise mongoengine.ValidationError('Not enough balance in fund {}'.format(fund.name))

        new_fund_transaction = FundTransaction(change=self.total_change,
                                               assigment=1,
                                               fund=fund)

        self.fund_transactions.append(new_fund_transaction)


    @classmethod
    def pre_save_post_validation(cls, sender, document: 'Transaction', created):
        if document.is_income():
            document.__proccess_income()
        else:
            document.__process_expense()

        assert 0.99 <= sum([ft.assigment for ft in document.fund_transactions]) <= 1 # for the moment a margin of 0.01 es accepted
        assert sum([ft.change for ft in document.fund_transactions]) == document.total_change


signals.pre_save_post_validation.connect(Transaction.pre_save_post_validation, sender=Transaction)
