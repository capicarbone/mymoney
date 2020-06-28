import pytest
import mongoengine
import os
from models.user import User

@pytest.fixture(scope="module")
def db():
    mongoengine.connect('mymoney_test', host=os.environ.get('MONGODB_TEST_URI', 'mongodb://localhost/mymoney_test'))
    return mongoengine.get_connection()

@pytest.fixture()
def user():
    return User.objects.first()