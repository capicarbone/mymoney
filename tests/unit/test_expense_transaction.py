
from .fixtures import *
import pytest
import mongoengine
from decimal import Decimal
from models.expense_transaction import ExpenseTransaction
from models.account import Account
from models.fund import Fund
import datetime

def test_valid_creation_for_expense_transaction(db, mongodb, user):
    account = Account.objects(owner=user)[0]
    fund = Fund.objects(is_default=False)[0]
    change = -322.01

    expense = ExpenseTransaction(account_id=account.id, change=change, date_accomplished=datetime.date.today(),
                                 category=fund.categories[0],
                                 owner=user)
    expense.save()

    assert len(expense.account_transactions) == 1
    assert len(expense.fund_transactions) == 1
    assert expense.account_transactions[0].change == expense.fund_transactions[0].change
    assert expense.fund_transactions[0].change == Decimal(change).quantize(Decimal('1.00'))

@pytest.mark.parametrize( ('attrs'), [
    {'change': 300, 'date_accomplished': datetime.datetime.now()},
    {'change': -300, 'date_accomplished': datetime.datetime.now(), 'category': None},
    {'change': -300, 'date_accomplished': datetime.datetime.now(), 'account_id': None}
])
def test_invalid_creation_for_expense_transaction(db, mongodb, user, attrs):
    attrs['owner'] = user
    attrs['account_id'] = Account.objects(owner=user)[0].id if 'account_id' not in attrs else None
    attrs['category'] = Fund.objects(is_default=False)[0].categories[0] if 'category' not in attrs else None

    expense = ExpenseTransaction(**attrs)

    with pytest.raises(mongoengine.ValidationError):
        expense.save()

@pytest.mark.parametrize(('change'), [-0.5, -2, -233.12, -1333.33, -20000, -100000, -1000000])
def test_valid_change_adjustment(db, mongodb, user, change):
    expense = ExpenseTransaction.objects(owner=user).first()

    expense.adjust_change(change)

    assert len(expense.account_transactions) == 1
    assert expense.account_transactions[0].change == Decimal(change).quantize(Decimal('1.00'))
    assert sum([t.change for t in expense.account_transactions]) == Decimal(change).quantize(Decimal('1.00'))

@pytest.mark.parametrize(('change'), [0, 200])
def test_invalid_change_adjustment(db, mongodb, user, change):
    expense = ExpenseTransaction.objects(owner=user).first()

    with pytest.raises(mongoengine.ValidationError):
        expense.adjust_change(change)




