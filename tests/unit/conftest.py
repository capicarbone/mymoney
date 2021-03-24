import pytest
import mongoengine
import os
from models.user import User

@pytest.fixture(scope="module")
def db(pytestconfig):
    mongoengine.connect('mymoney_test', host=pytestconfig.getini('mongodb_host'))
    yield mongoengine.get_connection()
    mongoengine.disconnect()

@pytest.fixture()
def user():
    return User.objects.first()