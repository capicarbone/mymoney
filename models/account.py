from decimal import Decimal

import mongoengine
import datetime
from .user import User
from mongoengine.connection import get_db

class Account(mongoengine.Document):
    name = mongoengine.StringField(required=True, blank=False)
    owner = mongoengine.LazyReferenceField(User, required=True)
    created_at = mongoengine.DateTimeField(default=lambda: datetime.datetime.now())

    @property
    def balance(self) -> Decimal:
        db = get_db()

        pipeline = [
            {'$unwind': '$account_transactions'},
            {'$match': {'owner': self.owner.id, 'account_transactions.account': self.id}},
            {'$group': {'_id': '$account_transactions.account', 'balance': {'$sum': '$account_transactions.change'}}}
        ]

        try:
            result = db.transaction.aggregate(pipeline).next()
            return Decimal(result['balance']).quantize(Decimal('0.01'))
        except StopIteration as e:
            return Decimal(0.0)



