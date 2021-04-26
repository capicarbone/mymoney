from decimal import Decimal

import mongoengine
from .user import User
from .account import Account
from .category import TransactionCategory
from .fund import Fund


def is_positive(x):
    if x < 0:
        raise mongoengine.ValidationError('income can not be negative')


def is_negative(x):
    if x > 0:
        raise mongoengine.ValidationError('expense can not be positive')


class EntityChange(mongoengine.EmbeddedDocument):
    income = mongoengine.DecimalField(required=True, default=Decimal(0.0), validation=is_positive)
    expense = mongoengine.DecimalField(required=True, default=Decimal(0.0), validation=is_negative)

    meta = {'allow_inheritance': True}

    def apply(self, change: Decimal, reverse=False):
        if reverse:
            if change > 0:
                self.income -= change
            else:
                self.expense -= change
        else:
            if change > 0:
                self.income += change
            else:
                self.expense += change

    @property
    def change(self):
        return self.income + self.expense


class AccountChange(EntityChange):
    account = mongoengine.LazyReferenceField(Account, required=True)


class CategoryChange(EntityChange):
    category = mongoengine.LazyReferenceField(TransactionCategory, required=True)



class FundChange(EntityChange):
    fund = mongoengine.LazyReferenceField(Fund, required=True)

class PeriodStatement(mongoengine.Document):
    month = mongoengine.IntField(required=True, choices=list(range(1, 13)))
    year = mongoengine.IntField(required=True)
    owner = mongoengine.LazyReferenceField(User, required=True)
    accounts = mongoengine.EmbeddedDocumentListField(AccountChange)
    categories = mongoengine.EmbeddedDocumentListField(CategoryChange)
    funds = mongoengine.EmbeddedDocumentListField(FundChange)
    last_transaction_processed = mongoengine.LazyReferenceField('Transaction', required=True)

    @property
    def total_change(self) -> Decimal:
        return sum([acc.income + acc.expense for acc in self.accounts])

    def get_cateogry_change(self, category_id: str) -> CategoryChange:
        search = [cat for cat in self.categories if cat.category.id == category_id]

        return search[0] if len(search) == 1 else None

    def get_account_change(self, account_id: str) -> AccountChange:
        search = [acc for acc in self.accounts if acc.account.id == account_id]

        return search[0] if len(search) == 1 else None

    def get_fund_change(self, fund_id: str) -> FundChange:
        search = [fnd for fnd in self.funds if fnd.fund.id == fund_id]

        return search[0] if len(search) == 1 else None

    def adjust(self, transaction: 'Transaction', reverse=False):
        category_change = self.get_cateogry_change(transaction.category.id)

        if category_change is None:
            category_change = CategoryChange(category=transaction.category)
            self.categories.insert(0, category_change)

        category_change.apply(transaction.total_change, reverse)

        account = transaction.account_transactions[0].account
        account_change = self.get_account_change(account.id)

        if account_change is None:
            account_change = AccountChange(account=account)
            self.accounts.insert(0, account_change)

        account_change.apply(transaction.total_change, reverse)

        for fund_transaction in transaction.fund_transactions:
            fund_change = self.get_fund_change(fund_transaction.fund.id)

            if fund_change is None:
                fund_change = FundChange(fund=fund_transaction.fund)
                self.funds.insert(0, fund_change)

            fund_change.apply(fund_transaction.change, reverse)

    @classmethod
    def add_to_statement(cls, transaction: 'Transaction'):
        if transaction.is_transfer():
            return

        try:
            month_statement = PeriodStatement.objects(owner=transaction.owner,
                                                      month=transaction.date_accomplished.month,
                                                      year=transaction.date_accomplished.year).get()
        except mongoengine.DoesNotExist:
            month_statement = PeriodStatement(owner=transaction.owner,
                                              month=transaction.date_accomplished.month,
                                              year=transaction.date_accomplished.year)

        month_statement.adjust(transaction)

        month_statement.last_transaction_processed = transaction.id
        month_statement.save()

    @classmethod
    def remove_from_statement(cls, transaction: 'Transaction'):
        month_statement = PeriodStatement.objects(owner=transaction.owner,
                                                  month=transaction.date_accomplished.month,
                                                  year=transaction.date_accomplished.year).get()

        month_statement.adjust(transaction, reverse=True)

        month_statement.save()

    @classmethod
    def transaction_post_save(cls, sender, document: 'Transaction', created: bool):
        if created and not document.is_transfer():
            cls.add_to_statement(document)

    @classmethod
    def transaction_post_delete(cls, sender, document: 'Transaction'):
        cls.remove_from_statement(document)
