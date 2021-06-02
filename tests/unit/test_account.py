import datetime
import pytest
from decimal import Decimal
from models import Account, ExpenseTransaction, IncomeTransaction


@pytest.fixture()
def create_and_load_transactions(db, mongodb, main_user_id, expense_categories, income_category):
    initial_balance = 4303
    account = Account(owner=main_user_id, name="New Account",
                      initial_balance=initial_balance
                      )
    account.save()

    ExpenseTransaction(owner=main_user_id,
                       date_accomplished=datetime.datetime.now(),
                       category=expense_categories[0],
                       change=-200,
                       account_id=account.id) \
        .save()

    IncomeTransaction(
        owner=main_user_id,
        date_accomplished=datetime.datetime.now(),
        category=income_category,
        change=500,
        account_id=account.id) \
        .save()

    # yes, I could not hardcode the changes, sorry
    return account.id, [4303, -200, 500]


def test_account_balance_calculation(db, mongodb):
    account = Account.objects(id="5ec7441e192cf1720a170389").get()
    assert account.balance == Decimal(1950)

    account = Account.objects(id="5ec74423192cf1720a17038a").get()
    assert account.balance == Decimal(1900)


def test_initial_balance_existance(db, mongodb, user):
    account = Account(name='My wallet', owner=user)
    account.save()

    assert account.initial_balance == 0

    initial_balance = 200
    account = Account(name='My wallet 2', owner=user, initial_balance=initial_balance)

    assert account.initial_balance == initial_balance


def test_initial_balance_computed_on_account_balance(create_and_load_transactions):
    account_id, changes = create_and_load_transactions
    expected_balance = sum(changes)

    account = Account.objects(id=account_id).get()

    assert account.balance == expected_balance
