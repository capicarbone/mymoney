from decimal import Decimal
from enum import Enum

import mongoengine
from mongoengine.queryset.visitor import Q
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


class StatementLevel(Enum):
    MONTH = 3
    YEAR = 2
    GENERAL = 1


class StatementQuerySet(mongoengine.QuerySet):

    def all_levels(self, month: int, year: int):
        return self.filter(Q(level=StatementLevel.GENERAL)
                    | Q(month=month, year=year, level=StatementLevel.MONTH)
                    | Q(year=year, level=StatementLevel.YEAR))


class Statement(mongoengine.Document):
    meta = {'queryset_class': StatementQuerySet}

    month = mongoengine.IntField(choices=list(range(1, 13)))
    year = mongoengine.IntField()
    level = mongoengine.EnumField(required=True, enum=StatementLevel)
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
    def add_to_statements(cls, transaction: 'Transaction'):
        if transaction.is_transfer():
            return

        statements = list(Statement.objects.all_levels(month=transaction.date_accomplished.month,
                                                  year=transaction.date_accomplished.year))

        available_levels = [statement.level for statement in statements]

        if StatementLevel.MONTH not in available_levels:
            month_statement = Statement(owner=transaction.owner,
                                        level=StatementLevel.MONTH,
                                        month=transaction.date_accomplished.month,
                                        year=transaction.date_accomplished.year)
            statements.append(month_statement)

        if StatementLevel.YEAR not in available_levels:
            year_statement = Statement(owner=transaction.owner,
                                        level=StatementLevel.YEAR,
                                        month=None,
                                        year=transaction.date_accomplished.year)
            statements.append(year_statement)

        if StatementLevel.GENERAL not in available_levels:
            general_statement = Statement(owner=transaction.owner,
                                        level=StatementLevel.GENERAL,
                                        month=None,
                                        year=None)
            statements.append(general_statement)

        for statement in statements:
            statement.adjust(transaction)
            statement.last_transaction_processed = transaction.id
            statement.save()

    @classmethod
    def remove_from_statements(cls, transaction: 'Transaction'):
        statements = list(Statement.objects.all_levels(month=transaction.date_accomplished.month,
                                                       year=transaction.date_accomplished.year))

        for statement in statements:
            statement.adjust(transaction, reverse=True)
            statement.save()

    @classmethod
    def transaction_post_save(cls, sender, document: 'Transaction', created: bool):
        if created and not document.is_transfer():
            cls.add_to_statements(document)

    @classmethod
    def transaction_post_delete(cls, sender, document: 'Transaction'):
        cls.remove_from_statements(document)
