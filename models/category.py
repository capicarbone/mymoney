import mongoengine
import datetime
from .user import User

CATEGORY_TYPES = (
    'expense',
    'income'
)

class TransactionCategory(mongoengine.Document):

    owner = mongoengine.LazyReferenceField(User, required=True)
    type = mongoengine.StringField(choices=CATEGORY_TYPES) # Validate that is required if category
    name = mongoengine.StringField(max_length=25)
    parent = mongoengine.ReferenceField('self')
    created_at = mongoengine.DateTimeField(default=lambda: datetime.datetime.now())

    def get_subcategories(self):
        return TransactionCategory.objects(parent=self, owner=self.owner)

    def clean(self):
        if not self.parent and not self.type:
            raise mongoengine.ValidationError('type field required')
