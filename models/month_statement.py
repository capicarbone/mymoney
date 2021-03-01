
import mongoengine
from .user import User
from .account import Account
from .category import TransactionCategory
from .fund import Fund
from .transaction import Transaction


class AccountChange(mongoengine.EmbeddedDocument):
    account = mongoengine.LazyReferenceField(Account, required=True)
    income = mongoengine.DecimalField(required=True, default=0.0)
    expense = mongoengine.DecimalField(required=True, default=0.0)


class CategoryChange(mongoengine.EmbeddedDocument):
    category = mongoengine.LazyReferenceField(TransactionCategory, required=True)
    change = mongoengine.DecimalField(required=True)


class FundChange(mongoengine.EmbeddedDocument):
    fund = mongoengine.LazyReferenceField(Fund, required=True)
    income = mongoengine.DecimalField(required=True, default=0.0)
    expense = mongoengine.DecimalField(required=True, default=0.0)


class MonthStatement(mongoengine.Document):
    month = mongoengine.IntField(required=True, choices=list(range(1, 12)))
    year = mongoengine.IntField(required=True)
    owner = mongoengine.LazyReferenceField(User, required=True)
    accounts = mongoengine.EmbeddedDocumentListField(AccountChange)
    categories = mongoengine.EmbeddedDocumentListField(CategoryChange)
    funds = mongoengine.EmbeddedDocumentListField(FundChange)
    last_transaction_processed = mongoengine.LazyReferenceField(Transaction)

    def get_cateogry_change(self, category_id: str):
        search = [cat for cat in self.categories if cat.category == category_id]

        if len(search) == 1:
            return search[0]
        else:
            return None

