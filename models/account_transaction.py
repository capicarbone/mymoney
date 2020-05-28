
import mongoengine
from models.account import  Account

class AccountTransaction(mongoengine.EmbeddedDocument):
    id = mongoengine.ObjectIdField()
    account = mongoengine.ReferenceField(Account, required=True)
    change = mongoengine.DecimalField(default=0)
