import mongoengine
from mongoengine import signals
import uuid
from models.fund import Fund
import datetime


class User(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    email = mongoengine.EmailField(required=True, unique=True)
    password_hash = mongoengine.StringField(required=True)
    auth_token = mongoengine.StringField(default= lambda: str(uuid.uuid4()), unique=True)
    created_at = mongoengine.DateTimeField(default=lambda: datetime.datetime.now())

    @classmethod
    def post_save(cls, sender, document, created):
        if created is True:
            fund = Fund(owner=document,
                        name="Free",
                        description="Default fund",
                        percentage_assignment=0,
                        is_default=True)
            fund.save()

signals.post_save.connect(User.post_save, sender=User)
