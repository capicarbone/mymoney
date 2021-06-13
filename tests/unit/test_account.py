import datetime
import pytest
from decimal import Decimal
from models import Account, ExpenseTransaction, IncomeTransaction, InitialBalanceTransaction, Fund

def test_account_balance_calculation(db, mongodb):
    account = Account.objects(id="5ec7441e192cf1720a170389").get()
    assert account.balance == Decimal(1950)

    account = Account.objects(id="5ec74423192cf1720a17038a").get()
    assert account.balance == Decimal(1900)
