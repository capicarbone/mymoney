import mongoengine
import datetime

CATEGORY_KINDS = (
    'expense',
    'income'
)

class TransactionCategory(mongoengine.Document):

    owner = mongoengine.LazyReferenceField('User', required=True)
    name = mongoengine.StringField(max_length=25)
    kind = mongoengine.StringField(choices=CATEGORY_KINDS, default=CATEGORY_KINDS[0], required=True)
    created_at = mongoengine.DateTimeField(default=lambda: datetime.datetime.now())

    def is_income(self):
        return self.kind == 'income'

