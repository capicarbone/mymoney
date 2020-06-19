
import datetime
import mongoengine
from decimal import Decimal
import pytest
from .fixtures import *
from models.fund import Fund
from models.income_transaction import IncomeTransaction
from models.account import Account

@pytest.mark.parametrize(('change'), [0.5, 2, 233.12, 1333.33, 20000, 100000, 1000000])
def test_valid_creation_for_income_transaction(db, mongodb, user, change):
    account = Account.objects(owner=user)[0]

    income = IncomeTransaction(owner=user, account_id=account.id, change=change,
                               time_accomplished=datetime.datetime.now())

    income.save()

    funds_count = Fund.objects(owner=user, is_active=True).count()

    assert len(income.account_transactions) == 1
    assert income.account_transactions[0].change == Decimal(change).quantize(Decimal('1.00'))
    assert sum([t.change for t in income.account_transactions ]) == Decimal(change).quantize(Decimal('1.00'))
    assert len(income.fund_transactions) == funds_count

@pytest.mark.parametrize(('change'), [0.5, 2, 233.12, 1333.33, 20000, 100000, 1000000])
def test_valid_change_adjustment(db, mongodb, user, change):
    income : IncomeTransaction = IncomeTransaction.objects(owner=user).first()

    income.adjust_change(change)

    assert len(income.account_transactions) == 1
    assert income.account_transactions[0].change == Decimal(change).quantize(Decimal('1.00'))
    assert sum([t.change for t in income.account_transactions]) == Decimal(change).quantize(Decimal('1.00'))

@pytest.mark.parametrize(('change'), [0, -200])
def test_invalid_change_adjustment(db, mongodb, user, change):
    income : IncomeTransaction = IncomeTransaction.objects(owner=user).first()

    with pytest.raises(mongoengine.ValidationError):
        income.adjust_change(change)
