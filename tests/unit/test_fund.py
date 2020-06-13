
from models.fund import Fund
from models.user import User
import mongoengine
import pytest
from decimal import Decimal

@pytest.fixture(scope="module")
def db():
    mongoengine.connect('mymoney_test')
    return mongoengine.get_connection()

@pytest.fixture()
def user():
    return User.objects.first()

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

@pytest.mark.parametrize( ('attr'), [
    {'percentage_assigment': 0.1},
    {'name': 'Test fund', 'percentage_assigment': 0.1, 'minimum_limit': 500, 'maximum_limit': 100}
])
def test_invalid_attributes_insert(db, mongodb, attr):
    attr['owner'] = User.objects.first()
    f = Fund(**attr)
    with pytest.raises(mongoengine.ValidationError):
        f.save()

def test_valid_insert(db, mongodb):
    attr = {'name': 'Test Fund','percentage_assigment': 0.1, 'owner': User.objects.first() }
    f = Fund(**attr)
    f.save()
    assert Fund.objects(name=attr["name"]).get() is not None

def test_fund_balance(db, mongodb):
    fund = Fund.objects(id="5ec741e6192cf1720a170378").get()
    assert fund.balance == Decimal(1333.34).quantize(Decimal('1.00'))



