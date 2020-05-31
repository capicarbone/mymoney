
import mongoengine
from models.fund import Fund

class FundTransaction(mongoengine.EmbeddedDocument):
    fund = mongoengine.LazyReferenceField(Fund, required=True)
    change = mongoengine.DecimalField(required=True)
