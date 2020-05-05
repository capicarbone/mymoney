import mongoengine
import datetime
from .user import User

class Account(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    owner = mongoengine.LazyReferenceField(User, required=True)
    created_at = mongoengine.DateTimeField(default=lambda: datetime.datetime.now())
