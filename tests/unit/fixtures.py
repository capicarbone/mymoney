import pytest
import mongoengine
from models.user import User

@pytest.fixture(scope="module")
def db():
    mongoengine.connect('mymoney_test')
    return mongoengine.get_connection()

@pytest.fixture()
def user():
    return User.objects.first()