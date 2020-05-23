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
        default_fund: Fund = None
        remaining = self.change
        total_adjustment = 0.0

        funds_in_deficit = [fund for fund in funds if fund.get_deficit() > 0]

        total_deficit = sum([fund.get_deficit() for fund in funds_in_deficit])

        # Making assigment on funds with deficit, must be the priority
        for fund in funds_in_deficit:

            to_assign: float = self.change * fund.percentage_assigment

            if total_deficit > self.change:
                to_assign = self.change / len(funds_in_deficit)
            else:
                if to_assign < fund.get_deficit():
                    adjustment = fund.get_deficit() - to_assign
                    to_assign = to_assign + adjustment
                    total_adjustment = total_adjustment + adjustment
                else:
                    if fund.maximum_limit and to_assign + fund.get_balance() > fund.maximum_limit:
                        to_assign = to_assign - ((to_assign + fund.get_balance()) - fund.maximum_limit)

            fund_transaction = FundTransaction(change=to_assign,
                                               assigment=to_assign / self.change,
                                               fund=fund)
            self.fund_transactions.append(fund_transaction)
            remaining = remaining - to_assign

            print("To assign " + str(to_assign))
            print("remaining is " + str(remaining))

        print("Total deficit " + str(total_deficit))
        assert 0 <= remaining <= self.change

        # Taking funds that does not have assigment yet
        funds_for_assignment = [fund for fund in funds if not next((t for t in self.fund_transactions if t.fund == fund),None)]

        if remaining > 0.009:
            adjustment = total_adjustment / len(funds_for_assignment)
            for fund in funds_for_assignment:

                if fund.is_default:
                    default_fund = fund
                    continue

                if fund.maximum_limit is not None and fund.get_balance() >= fund.maximum_limit:
                    continue

                to_assign = (self.change * fund.percentage_assigment) - adjustment

                f_transaction = FundTransaction(change=to_assign,
                                                assigment=to_assign / self.change,
                                                fund=fund)
                self.fund_transactions.append(f_transaction)
                remaining = remaining - to_assign

        print("remaining is " + str(remaining))
        assert 0 <= remaining < self.change

        if remaining > 0.009:
            fund_transaction = FundTransaction(change=remaining,
                                               assigment=remaining / self.change,
                                               fund=default_fund)
            self.fund_transactions.append(fund_transaction)
            remaining = remaining - remaining

        assert sum([ft.assigment for ft in self.fund_transactions]) <= 1
        assert remaining <= 0.01

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
