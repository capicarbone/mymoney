import mongoengine
import datetime
from .user import User

CATEGORY_TYPES = (
    'expense',
    'income'
)

class FundCategory(mongoengine.Document):

    owner = mongoengine.LazyReferenceField(User, required=True)
    name = mongoengine.StringField(max_length=25)
    created_at = mongoengine.DateTimeField(default=lambda: datetime.datetime.now())

