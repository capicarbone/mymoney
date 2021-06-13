import datetime
import pytest
from models import Account, InitialBalanceTransaction, IncomeTransaction, ExpenseTransaction, Fund


@pytest.fixture()
def create_and_load_transactions(db, mongodb, main_user_id, expense_categories, income_category):
    account = Account(owner=main_user_id, name="New Account",
                      )
    account.save()

    InitialBalanceTransaction(owner=main_user_id,
                              change=4303,
                              account_id=account.id).save()

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


def test_initial_balance_computed_on_account_balance(create_and_load_transactions, main_user_id):
    account_id, changes = create_and_load_transactions
    expected_balance = sum(changes)

    account = Account.objects(id=account_id).get()
    fund = Fund.objects(owner=main_user_id, is_default=True).get()

    assert account.balance == expected_balance
    assert fund.balance == changes[0] # The initial balance should be assigned to default fund

def test_initial_balance_computed_on_general_balance(create_and_load_transactions, main_user_id):
    pass

    # TODO Implement
