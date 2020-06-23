
import mongoengine
from models.fund import Fund

class FundTransaction(mongoengine.EmbeddedDocument):
    fund = mongoengine.LazyReferenceField(Fund, required=True)
    change = mongoengine.DecimalField(required=True)

    def __unicode__(self):
        return "For fund {} is assigned {}".format(self.fund.fetch().name, self.change)
