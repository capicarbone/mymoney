
from .fixtures import *
from decimal import Decimal
from models.expense_transaction import ExpenseTransaction
from models.account import Account
from models.fund import Fund
import datetime

def test_valid_creation_for_expense_transaction(db, mongodb, user):
    account = Account.objects(owner=user)[0]
    fund = Fund.objects(is_default=False)[0]
    change = 322.01

    expense = ExpenseTransaction(account_id=account.id, change=change, time_accomplished=datetime.datetime.now(),
                                 category=fund.categories[0],
                                 owner=user)
    expense.save()

    assert len(expense.account_transactions) == 1
    assert len(expense.fund_transactions) == 1
    assert expense.account_transactions[0].change == expense.fund_transactions[0].change
    assert expense.fund_transactions[0].change == Decimal(change).quantize(Decimal('1.00'))


