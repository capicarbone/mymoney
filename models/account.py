import mongoengine
import datetime
from .user import User
from mongoengine.connection import get_db

class Account(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    owner = mongoengine.LazyReferenceField(User, required=True)
    created_at = mongoengine.DateTimeField(default=lambda: datetime.datetime.now())

    def get_balance(self) -> float:
        db = get_db()

        pipeline = [
            {'$match': {'account': self.id, 'owner': self.owner.id}},
            {'$group': {'_id': '$account', 'balance': {'$sum': '$change'}}}
        ]

        try:
            result = db.transaction.aggregate(pipeline).next()
            return result['balance']
        except StopIteration as e:
            return 0



