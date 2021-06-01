
from decimal import Decimal
from models.account import Account

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

# TODO balance calculation takes in account the initial balance.