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

