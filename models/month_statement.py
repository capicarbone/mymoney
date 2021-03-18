from decimal import Decimal

import mongoengine
from .user import User
from .account import Account
from .category import TransactionCategory
from .fund import Fund


class AccountChange(mongoengine.EmbeddedDocument):
    account = mongoengine.LazyReferenceField(Account, required=True)
    income = mongoengine.DecimalField(required=True, default=Decimal(0.0))
    expense = mongoengine.DecimalField(required=True, default=Decimal(0.0))


class CategoryChange(mongoengine.EmbeddedDocument):
    category = mongoengine.LazyReferenceField(TransactionCategory, required=True)
    change = mongoengine.DecimalField(required=True, default=Decimal(0.0))


class FundChange(mongoengine.EmbeddedDocument):
    fund = mongoengine.LazyReferenceField(Fund, required=True)
    income = mongoengine.DecimalField(required=True, default=Decimal(0.0))
    expense = mongoengine.DecimalField(required=True, default=Decimal(0.0))


class MonthStatement(mongoengine.Document):
    month = mongoengine.IntField(required=True, choices=list(range(1, 12)))
    year = mongoengine.IntField(required=True)
    owner = mongoengine.LazyReferenceField(User, required=True)
    accounts = mongoengine.EmbeddedDocumentListField(AccountChange)
    categories = mongoengine.EmbeddedDocumentListField(CategoryChange)
    funds = mongoengine.EmbeddedDocumentListField(FundChange)
    last_transaction_processed = mongoengine.LazyReferenceField('Transaction', required=True)

    def get_cateogry_change(self, category_id: str):
        search = [cat for cat in self.categories if cat.category.id == category_id]

        return search[0] if len(search) == 1 else None

    def get_account_change(self, account_id: str):
        search = [acc for acc in self.accounts if acc.account.id == account_id]

        return search[0] if len(search) == 1 else None

    def get_fund_change(self, fund_id: str):
        search = [fnd for fnd in self.funds if fnd.fund.id == fund_id]

        return search[0] if len(search) == 1 else None

    def adjust(self, transaction: 'Transaction'):
        category_change = self.get_cateogry_change(transaction.category.id)

        if category_change is None:
            category_change = CategoryChange(category=transaction.category)
            self.categories.insert(0, category_change)

        category_change.change += transaction.total_change

        account = transaction.account_transactions[0].account
        account_change = self.get_account_change(account.id)

        if account_change is None:
            account_change = AccountChange(account=account)
            self.accounts.insert(0, account_change)

        if transaction.total_change > 0:
            account_change.income += transaction.total_change
        else:
            account_change.expense += transaction.total_change

        for fund_transaction in transaction.fund_transactions:
            fund_change = self.get_fund_change(fund_transaction.fund)

            if fund_change is None:
                fund_change = FundChange(fund=fund_transaction.fund)
                self.funds.insert(0, fund_change)

            if fund_transaction.change > 0:
                fund_change.income += fund_transaction.change
            else:
                fund_change.expense += fund_transaction.change

    @classmethod
    def add_to_statement(cls, transaction: 'Transaction'):
        if transaction.is_transfer():
            return

        try:
            month_statement = MonthStatement.objects(owner=transaction.owner,
                                                     month=transaction.date_accomplished.month,
                                                     year=transaction.date_accomplished.year).get()
        except mongoengine.DoesNotExist:
            month_statement = MonthStatement(owner=transaction.owner,
                                             month=transaction.date_accomplished.month,
                                             year=transaction.date_accomplished.year)

        month_statement.adjust(transaction)

        month_statement.last_transaction_processed = transaction.id
        month_statement.save()

    @classmethod
    def remove_from_statement(cls, transaction:'Transaction'):
        month_statement = MonthStatement.objects(owner=transaction.owner,
                                                 month=transaction.date_accomplished.month,
                                                 year=transaction.date_accomplished.year).get()

        month_statement.adjust(-transaction)

        month_statement.save()

    @classmethod
    def transaction_post_save(cls, sender, document: 'Transaction', created: bool):
        if created and not document.is_transfer():
            cls.add_to_statement(document)

    @classmethod
    def transaction_post_delete(cls, sender, document: 'Transaction'):
        cls.remove_from_statement(document)
