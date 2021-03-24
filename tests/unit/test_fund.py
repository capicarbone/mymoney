
import pytest
import mongoengine
from models.fund import Fund
from models.user import User
from decimal import Decimal
from datetime import datetime

def test_inser_with_invalid_percentage_assignment(db, mongodb, user):
    attr = {'name': 'Test Fund','percentage_assignment': -1, 'owner': user }
    f = Fund(**attr)

    with pytest.raises(mongoengine.ValidationError):
        f.save()

def test_insert_with_total_percentage_greater_than_1(db, mongodb, user):
    attr = {'name': 'Test Fund','percentage_assignment': 0.2, 'owner': user }
    f = Fund(**attr)

    with pytest.raises(mongoengine.ValidationError):
        f.save()

@pytest.mark.parametrize( ('attr'), [
    {'percentage_assignment': 0.1},
    {'name': 'Test fund', 'percentage_assignment': 0.1, 'minimum_limit': 500, 'maximum_limit': 100}
])
def test_invalid_attributes_insert(db, mongodb, attr):
    attr['owner'] = User.objects.first()
    f = Fund(**attr)
    with pytest.raises(mongoengine.ValidationError):
        f.save()

def test_valid_insert(db, mongodb):
    attr = {'name': 'Test Fund','percentage_assignment': 0.1, 'owner': User.objects.first() }
    f = Fund(**attr)
    f.save()
    assert Fund.objects(name=attr["name"]).get() is not None

def test_fund_balance(db, mongodb):
    fund = Fund.objects(id="5ec741e6192cf1720a170378").get()
    assert fund.balance == Decimal(1233.34).quantize(Decimal('1.00'))

def test_fund_balance_from(db, mongodb):
    fund = Fund.objects(id="5ec741e6192cf1720a170378").get()
    assert fund.balance_from(datetime(2020, 2, 1)) == Decimal(666.67).quantize(Decimal('1.00'))

def test_fund_deficit(db, mongodb):
    fund = Fund.objects(id="5ec741e6192cf1720a170378").get()
    assert fund.get_deficit() == Decimal(3766.66).quantize(Decimal('1.00'))

def test_fund_deficit_from(db, mongodb):
    fund = Fund.objects(id="5ec741e6192cf1720a170378").get()
    assert fund.get_deficit_from(datetime(2020, 2, 1)) == Decimal(4333.33).quantize(Decimal('1.00'))


