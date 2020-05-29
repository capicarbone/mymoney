
import mongoengine
from models.category import FundCategory
from mongoengine.connection import get_db
from decimal import Decimal

class FundQuerySet(mongoengine.QuerySet):

    def actives_for(self, owner):
        return self.filter(is_active=True, owner=owner)

    def default_for(self, owner) -> 'Fund':
        return self.filter(owner=owner, is_default=True).get()

class Fund(mongoengine.Document):
    owner = mongoengine.LazyReferenceField('User', required=True)
    name = mongoengine.StringField(required=True)
    description = mongoengine.StringField()
    minimum_limit = mongoengine.DecimalField()
    maximum_limit = mongoengine.DecimalField()
    percentage_assigment = mongoengine.DecimalField(required=True, precision=2, min_value=0, max_value=1)
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


    @property
    def balance(self) -> Decimal:
        db = get_db()

        pipeline = [
            {'$unwind': '$fund_transactions'},
            {'$match': {'owner': self.owner.id, 'fund_transactions.fund': self.id}},
            {'$group': {'_id': '$fund_transactions.fund', 'balance': {'$sum': '$fund_transactions.change'}}}
        ]

        try:
            result = db.transaction.aggregate(pipeline).next()
        except StopIteration:
            return Decimal(0.0)

        return Decimal(result['balance']).quantize(Decimal('0.01'))

    def get_deficit(self) -> Decimal:

        if self.minimum_limit is None:
            return Decimal(0.0)

        difference = self.minimum_limit - self.balance

        if difference > 0:
            return difference.quantize(Decimal('0.01'))
        else:
            return Decimal(0.0)

