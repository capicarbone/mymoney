
import mongoengine
from models.category import FundCategory
from mongoengine.connection import get_db

class FundQuerySet(mongoengine.QuerySet):

    def actives_for(self, owner) -> 'Fund':
        return self.filter(is_active=True, owner=owner)

class Fund(mongoengine.Document):
    owner = mongoengine.LazyReferenceField('User', required=True)
    name = mongoengine.StringField(required=True)
    description = mongoengine.StringField()
    minimum_limit = mongoengine.FloatField()
    maximum_limit = mongoengine.FloatField()
    percentage_assigment = mongoengine.FloatField(required=True)
    is_active = mongoengine.BooleanField(default=True)
    is_default = mongoengine.BooleanField(default=False)
    categories = mongoengine.ListField(mongoengine.ReferenceField(FundCategory))

    meta = {'queryset_class': FundQuerySet}

    def clean(self):

        total_assigment = Fund.objects(owner=self.owner).sum('percentage_assigment')

        if total_assigment + self.percentage_assigment > 1:
            raise mongoengine.ValidationError('Invalid percetange assigment')

        if self.minimum_limit and self.maximum_limit and self.minimum_limit >= self.maximum_limit:
            raise mongoengine.ValidationError('Minimun limit must be less than maximum limit.')


    def get_balance(self) -> float:
        db = get_db()

        pipeline = [
            {'$unwind': '$fund_transactions'},
            {'$match': {'owner': self.owner.id, 'fund_transactions.fund': self.id}},
            {'$group': {'_id': '$fund_transactions.fund', 'balance': {'$sum': '$fund_transactions.change'}}}
        ]

        try:
            result = db.transaction.aggregate(pipeline).next()
        except StopIteration:
            return 0

        return result['balance']

