
import mongoengine
from .user import User
from .account import Account
from .category import TransactionCategory
from .fund import Fund


class AccountChange(mongoengine.EmbeddedDocument):
    account = mongoengine.LazyReferenceField(Account, required=True)
    change = mongoengine.DecimalField(required=True)


class CategoryChange(mongoengine.EmbeddedDocument):
    category = mongoengine.LazyReferenceField(TransactionCategory, required=True)
    change = mongoengine.DecimalField(required=True)


class FundChange(mongoengine.EmbeddedDocument):
    fund = mongoengine.LazyReferenceField(Fund, required=True)
    change = mongoengine.DecimalField(required=True)


class MonthStatement(mongoengine.Document):
    month = mongoengine.IntField(required=True, choices=list(range(1, 12)))
    year = mongoengine.IntField(required=True)
    owner = mongoengine.LazyReferenceField(User, required=True)
    accounts = mongoengine.EmbeddedDocumentListField(AccountChange)
    categories = mongoengine.EmbeddedDocumentListField(CategoryChange)
    funds = mongoengine.EmbeddedDocumentListField(FundChange)

    def get_cateogry_change(self, category_id: str):
        search = [cat for cat in self.categories if cat.category == category_id]

        if len(search) == 1:
            return search[0]
        else:
            return None

