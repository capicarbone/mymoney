from decimal import Decimal

from .fixtures import *
import datetime
import mongoengine
import pytest
from models.account import Account
from models.category import TransactionCategory
from models.income_transaction import IncomeTransaction
from models.expense_transaction import ExpenseTransaction
from models.month_statement import MonthStatement


@pytest.mark.parametrize(('change',), [(Decimal("-300.00"),), (Decimal("300.00"),), (Decimal("2000.21"),), (Decimal("-1.23"),)])
def test_new_transaction_generates_new_month_statement(db, mongodb, user, change):
    account = Account.objects(owner=user)[0]

    income_category = TransactionCategory.objects(kind="income")[0]
    expense_category = TransactionCategory.objects(kind="expense")[0]

    transaction_date = datetime.date(2021, 2, 12)

    if change > 0:
        transaction = IncomeTransaction(owner=user, account_id=account.id, change=change,
                                        category=income_category.id,
                                        date_accomplished=transaction_date)
    else:
        transaction = ExpenseTransaction(owner=user, account_id=account.id, change=change,
                                         category=expense_category.id,
                                         date_accomplished=transaction_date)

    transaction.save()

    statement = None
    try:
        statement = MonthStatement.objects(owner=user,
                                           month=transaction_date.month,
                                           year=transaction_date.year).get()
    except mongoengine.DoesNotExist:
        pass

    assert statement is not None
    assert len(statement.categories) == 1
    assert len(statement.accounts) == 1
    assert len(statement.funds) > 0

    assert statement.categories[0].change == change

    if change > 0:
        assert statement.categories[0].category.id == income_category.id
    else:
        assert statement.categories[0].category.id == expense_category.id

    assert statement.accounts[0].income + statement.accounts[0].expense == change
    assert statement.accounts[0].account.id == account.id

    assert sum([fund_change.income + fund_change.expense for fund_change in statement.funds]) == change

    if change > 0:
        assert statement.accounts[0].expense == 0
        assert sum([fund_change.expense for fund_change in statement.funds]) == 0
    else:
        assert statement.accounts[0].income == 0
        assert sum([fund_change.income for fund_change in statement.funds]) == 0


@pytest.mark.parametrize(('changes'), [
    ([Decimal("-100.00"), Decimal("300"), Decimal("500")]),
    ([Decimal("-222.00"), Decimal("400"), Decimal("-500")]),
    ([Decimal("-211.12"), Decimal("12.1"), Decimal("500.00"), Decimal("451.00"), Decimal("723.99")]),
])
def test_new_transaction_updates_existing_month_statement(db, mongodb, user, changes):
    account = Account.objects(owner=user)[0]

    income_category = TransactionCategory.objects(kind="income")[0]
    expense_category = TransactionCategory.objects(kind="expense")[0]

    transaction_date = datetime.date(2021, 2, 12)

    for change in changes:

        if change > 0:
            transaction = IncomeTransaction(owner=user, account_id=account.id, change=change,
                               category=income_category,
                               date_accomplished=transaction_date)
        else:
            transaction = ExpenseTransaction(owner=user, account_id=account.id, change=change,
                               category=expense_category,
                               date_accomplished=transaction_date)

        transaction.save()

    statements = MonthStatement.objects(owner=user,
                                       month=transaction_date.month,
                                       year=transaction_date.year).all()
    assert len(statements) == 1
    statement = statements[0]

    total_income = sum([change for change in changes if change > 0])
    total_expense = sum(changes) - total_income
    total_balance = total_income + total_expense

    assert len(statement.categories) == 2
    for category_change in statement.categories:
        if category_change.category.id == expense_category.id:
            assert category_change.change == total_expense

        if category_change.category.id == income_category.id:
            assert category_change.change == total_income

    assert len(statement.accounts) == 1
    assert statement.accounts[0].income == total_income
    assert statement.accounts[0].expense == total_expense
    assert len(statement.funds) > 0
    assert sum([fund_change.income + fund_change.expense for fund_change in statement.funds]) == total_balance

    # TODO: Collect every fund transacion and validate against fund changes.
