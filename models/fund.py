
import mongoengine
from models.category import TransactionCategory
from mongoengine.connection import get_db
from decimal import Decimal
from datetime import datetime, date
from bson.objectid import ObjectId

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
    percentage_assignment = mongoengine.DecimalField(required=True, precision=2, min_value=0, max_value=1)
    is_active = mongoengine.BooleanField(default=True)
    is_default = mongoengine.BooleanField(default=False)
    categories = mongoengine.ListField(mongoengine.ReferenceField(TransactionCategory))

    meta = {'queryset_class': FundQuerySet}

    def clean(self):
        super().clean()

        total_assignment = Decimal(Fund.objects(owner=self.owner).sum('percentage_assignment'))

        if total_assignment + self.percentage_assignment > 1:
            raise mongoengine.ValidationError('Invalid percetange assignment')

        if self.minimum_limit and self.maximum_limit and self.minimum_limit >= self.maximum_limit:
            raise mongoengine.ValidationError('Minimun limit must be less than maximum limit.')


    @property
    def balance(self) -> Decimal:
        return self.balance_from(datetime.now())

    def balance_from(self, from_date: date, ignoring: ObjectId = None):
        db = get_db()

        from_datetime = datetime.combine(from_date, datetime.max.time())

        pipeline = [
            {'$unwind': '$fund_transactions'},
            {'$match':
                 {'owner': self.owner.id, 'date_accomplished': {'$lte': from_datetime}, 'fund_transactions.fund': self.id}},
            {'$group': {'_id': '$fund_transactions.fund', 'balance': {'$sum': '$fund_transactions.change'}}}
        ]

        if ignoring:
            pipeline[1]['$match']['id__ne'] = ignoring # TODO: IT should be improved for not depends of number index


        try:
            result = db.transaction.aggregate(pipeline).next()
        except StopIteration:
            return Decimal(0.0)

        return Decimal(result['balance']).quantize(Decimal('0.01'))

    def get_deficit_from(self, from_time, ignoring:ObjectId = None) -> Decimal:
        if self.minimum_limit is None:
            return Decimal(0.0)

        difference = self.minimum_limit - self.balance_from(from_time, ignoring)

        return difference.quantize(Decimal('0.01'))

    def get_deficit(self) -> Decimal:
        return self.get_deficit_from(datetime.now())


