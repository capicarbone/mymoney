from .fixtures import *
import datetime
import mongoengine
from models.account import Account
from models.category import TransactionCategory
from models.income_transaction import IncomeTransaction
from models.month_statement import MonthStatement


def test_new_transaction_generates_new_month_statement(db, mongodb, user):
    account = Account.objects(owner=user)[0]

    category = TransactionCategory.objects(kind="income")[0]

    year = 2021
    month = 2
    day = 12
    transaction_date = datetime.date(year, month, day)
    change = 300

    income = IncomeTransaction(owner=user, account_id=account.id, change=change,
                               category=category.id,
                               date_accomplished=transaction_date)

    income.save()

    statement = None
    try:
        statement = MonthStatement.objects(owner=user, month=month, year=year).get()
    except mongoengine.DoesNotExist:
        pass

    assert statement is not None
    assert len(statement.categories) == 1
    assert statement.categories[0].change == change
    assert len(statement.accounts) == 1
    assert statement.accounts[0].change == change
    assert len(statement.funds) == 1
    assert statement.funds == change
