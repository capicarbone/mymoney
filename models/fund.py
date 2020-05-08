
import mongoengine
from models.category import FundCategory
from models.user import User

class Fund(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    description = mongoengine.StringField()
    minimum_limit = mongoengine.FloatField()
    maximum_limit = mongoengine.FloatField()
    percentage_assigment = mongoengine.FloatField(required=True)
    categories = mongoengine.ListField(mongoengine.ReferenceField(FundCategory))
    owner = mongoengine.ReferenceField(User, required=True)

    def clean(self):

        total_assigment = Fund.objects(owner=self.owner).sum('percentage_assigment')

        if total_assigment + self.percentage_assigment > 1:
            raise mongoengine.ValidationError('Invalid percetange assigment')

        if self.minimum_limit >= self.maximum_limit:
            raise mongoengine.ValidationError('Minimun limit must be less than maximum limit.')