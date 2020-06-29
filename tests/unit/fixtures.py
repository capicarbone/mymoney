import pytest
import mongoengine
import os
from models.user import User

@pytest.fixture(scope="module")
def db(pytestconfig):
    #mongoengine.connect('mymoney_test', host=os.environ.get('MONGODB_TEST_URI', 'mongodb://localhost/mymoney_test'))
    mongoengine.connect('mymoney_test', host=pytestconfig.getini('mongodb_host'))
    return mongoengine.get_connection()

@pytest.fixture()
def user():
    return User.objects.first()