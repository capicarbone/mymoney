import pytest
import mongoengine
import os
from models.user import User

@pytest.fixture(scope="module")
def db(pytestconfig):
    mongoengine.connect('mymoney_test', host=pytestconfig.getini('mongodb_host'))
    yield mongoengine.get_connection()
    mongoengine.disconnect()

# TODO should need db and mongodb fixtures
@pytest.fixture()
def user():
    return User.objects.first()