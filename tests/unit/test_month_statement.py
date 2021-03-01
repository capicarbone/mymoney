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

    transaction_date = datetime.date(2021, 2, 12)
    change = 300

    income = IncomeTransaction(owner=user, account_id=account.id, change=change,
                               category=category.id,
                               date_accomplished=transaction_date)

    income.save()

    statement = None
    try:
        statement = MonthStatement.objects(owner=user,
                                           month=transaction_date.month,
                                           year=transaction_date.year).get()
    except mongoengine.DoesNotExist:
        pass

    assert statement is not None
    assert len(statement.categories) == 1
    assert statement.categories[0].change == change
    assert statement.categories[0].category == category.id
    assert len(statement.accounts) == 1
    assert statement.accounts[0].income == change
    assert statement.accounts[0].account == account.id
    assert len(statement.funds) > 0
    assert sum([fund_change.income for fund_change in statement.funds]) == change


def test_new_transaction_updates_existing_month_statement(db, mongodb, user):
    # TODO: Implement this with paramenteres supporting differente transactions
    account = Account.objects(owner=user)[0]

    category = TransactionCategory.objects(kind="income")[0]

    transaction_date = datetime.date(2021, 2, 12)
    change1 = 300

    income = IncomeTransaction(owner=user, account_id=account.id, change=change1,
                               category=category.id,
                               date_accomplished=transaction_date)

    income.save()

    change2 = 100
    income = IncomeTransaction(owner=user, account_id=account.id, change=change2,
                               category=category.id,
                               date_accomplished=transaction_date)

    income.save()

    statement = MonthStatement.objects(owner=user,
                                       month=transaction_date.month,
                                       year=transaction_date.year).get()

    assert len(statement.categories) == 1
    assert statement.categories[0].change == change1 + change2
    assert len(statement.accounts) == 1
    assert statement.accounts[0] == change1 + change2
    assert len(statement.funds) > 0
    assert sum([fund_change.income + fund_change.expense for fund_change in statement.funds]) == change1 + change2


