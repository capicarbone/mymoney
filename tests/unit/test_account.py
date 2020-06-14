
from .fixtures import *
from decimal import Decimal
from models.account import Account

def test_account(db, mongodb):
    account = Account.objects(id="5ec7441e192cf1720a170389").get()
    assert account.balance == Decimal(1950)

    account = Account.objects(id="5ec74423192cf1720a17038a").get()
    assert account.balance == Decimal(1900)
