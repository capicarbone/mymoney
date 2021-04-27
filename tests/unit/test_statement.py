from decimal import Decimal

from typing import List

from models import User
from models import StatementLevel, Statement
from models.transaction import Transaction

import datetime
import mongoengine
import pytest
from models.account import Account
from models.category import TransactionCategory
from models.income_transaction import IncomeTransaction
from models.expense_transaction import ExpenseTransaction



def not_repeated(items) -> bool:
    return len(set(items)) == len(items)


def is_consistent(month_statement: Statement):
    accounts_total_change = sum([acc.income + acc.expense for acc in month_statement.accounts])
    funds_total_change = sum([fnd.income + fnd.expense for fnd in month_statement.funds])
    categories_total_change = sum([cat.change for cat in month_statement.categories])

    accounts_not_repeated = not_repeated(
        [str(account_change.account.id) for account_change in month_statement.accounts]) is True
    categories_not_repeated = not_repeated(
        [str(category_change.category.id) for category_change in month_statement.categories]) is True
    funds_not_repeated = not_repeated([str(fund_change.fund.id) for fund_change in month_statement.funds]) is True

    return accounts_total_change == funds_total_change == categories_total_change and accounts_not_repeated and funds_not_repeated and categories_not_repeated


@pytest.fixture(params=[
    ([Decimal("1000.00"), Decimal("300"), Decimal("500")]),
    ([Decimal("-222.00"), Decimal("400"), Decimal("-500")]),
    ([Decimal("-211.12"), Decimal("12.1"), Decimal("500.00"), Decimal("-451.00"), Decimal("723.99")]),
])
def one_month_transactions(request, db, mongodb, user):
    account = Account.objects(owner=user)[0]

    income_category = TransactionCategory.objects(kind="income")[0]
    expense_category = TransactionCategory.objects(kind="expense")[0]

    transaction_date = datetime.date(2021, 2, 1)

    transactions = []

    for change in request.param:
        if change > 0:
            transaction = IncomeTransaction(owner=user, account_id=account.id, change=change,
                                            category=income_category,
                                            date_accomplished=transaction_date)
        else:
            transaction = ExpenseTransaction(owner=user, account_id=account.id, change=change,
                                             category=expense_category,
                                             date_accomplished=transaction_date)

        transaction.save()
        transactions.append(transaction)

    return transactions

def test_all_levels_query(user: User, one_month_transactions: List[Statement]):
    statements = Statement.objects.all_levels(month=2, year=2021)

    assert len(statements) == 3
    result_levels = [statement.level for statement in statements]
    for level in [StatementLevel.GENERAL, StatementLevel.YEAR, StatementLevel.MONTH]:
        assert level in result_levels

@pytest.mark.parametrize(('change',),
                         [(Decimal("-300.00"),), (Decimal("300.00"),), (Decimal("2000.21"),), (Decimal("-1.23"),)])
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
        statement = Statement.objects(owner=user,
                                      month=transaction_date.month,
                                      year=transaction_date.year).get()
    except mongoengine.DoesNotExist:
        pass

    assert statement is not None
    assert len(statement.categories) == 1
    assert len(statement.accounts) == 1
    assert len(statement.funds) > 0
    assert is_consistent(statement) is True

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

    statements = Statement.objects(owner=user,
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


def test_months_statements_consistency(user, one_month_transactions):
    transaction_date = one_month_transactions[0].date_accomplished
    expected_total_change = sum([t.total_change for t in one_month_transactions])
    statement = Statement.objects(month=transaction_date.month,
                                  year=transaction_date.year,
                                  owner=user).get()

    assert is_consistent(statement) is True
    assert expected_total_change == statement.total_change


def test_removed_transaction_changes_month_statement(user, one_month_transactions: List[Statement]):
    transaction_date = one_month_transactions[0].date_accomplished

    expected_total_change = sum([t.total_change for t in one_month_transactions])

    month_statement_query = Statement.objects(month=transaction_date.month,
                                              year=transaction_date.year,
                                              owner=user
                                              )

    for transaction in one_month_transactions:
        initial_month_statement: Statement = month_statement_query.get()

        tr: Transaction = Transaction.objects(
            id=transaction.id).get()  # Getting a transaction instance instead of a specialization
        total_change = tr.total_change
        tr.delete()

        month_statement: Statement = month_statement_query.get()

        expected_total_change -= total_change

        tr_account_id = tr.account_transactions[0].account.id

        assert is_consistent(month_statement)
        if tr.is_income():
            assert month_statement.get_account_change(
                tr_account_id).income == initial_month_statement.get_account_change(tr_account_id).income - \
                   tr.account_transactions[0].change

        if tr.is_expense():
            assert month_statement.accounts[0].expense == initial_month_statement.get_account_change(
                tr_account_id).expense - \
                   tr.account_transactions[0].change

        assert month_statement.total_change == expected_total_change
