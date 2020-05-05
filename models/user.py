import mongoengine
import uuid
import datetime

class User(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    email = mongoengine.EmailField(required=True, unique=True)
    password_hash = mongoengine.StringField(required=True)
    auth_token = mongoengine.StringField(default= lambda: str(uuid.uuid4()), unique=True)
    created_at = mongoengine.DateTimeField(default=lambda: datetime.datetime.now())