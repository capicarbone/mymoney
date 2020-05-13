import mongoengine
import datetime
from models.fund import Fund

class FundTransaction(mongoengine.EmbeddedDocument):
    fund = mongoengine.ReferenceField(Fund, required=True)
    change = mongoengine.FloatField(required=True)
    assigment = mongoengine.FloatField(required=True)
    balance = mongoengine.FloatField(required=True)
