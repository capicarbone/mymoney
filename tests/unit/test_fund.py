
from models.fund import Fund
from models.user import User
import mongoengine
import pytest

@pytest.fixture(scope="module")
def db():
    mongoengine.connect('mymoney_test')
    return mongoengine.get_connection()

@pytest.fixture()
def user():
    return User.objects.first()

def inc(x):
    return x + 1

def test_inser_with_invalid_percentage_assigment(db, mongodb, user):
    attr = {'name': 'Test Fund','percentage_assigment': -1, 'owner': user }
    f = Fund(**attr)

    with pytest.raises(mongoengine.ValidationError):
        f.save()

def test_insert_with_total_percentage_greater_than_1(db, mongodb, user):
    attr = {'name': 'Test Fund','percentage_assigment': 0.2, 'owner': user }
    f = Fund(**attr)

    with pytest.raises(mongoengine.ValidationError):
        f.save()

def test_valid_insert(db, mongodb):
    attr = {'name': 'Test Fund','percentage_assigment': 0.1, 'owner': User.objects.first() }
    f = Fund(**attr)
    f.save()
    assert f.id



