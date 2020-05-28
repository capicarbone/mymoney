
import mongoengine
from models.account import  Account

class AccountTransaction(mongoengine.EmbeddedDocument):
    account = mongoengine.ReferenceField(Account, required=True)
    change = mongoengine.DecimalField(default=0)
