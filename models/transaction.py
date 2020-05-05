import mongoengine
from flask_mongoengine import Document
import datetime
from .account import Account
from .category import TransactionCategory


class AccountTransaction(Document):
    description = mongoengine.StringField(max_length=50)
    account = mongoengine.ReferenceField(Account, required=True)
    time_accomplished = mongoengine.DateTimeField(required=True)
    change = mongoengine.FloatField(required=True)
    created_at = mongoengine.DateTimeField(default=lambda: datetime.datetime.now() )
    category = mongoengine.ReferenceField(TransactionCategory)

