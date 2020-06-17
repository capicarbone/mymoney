
from .fixtures import *
from decimal import Decimal
from models.accounts_transfer_transaction import AccountsTransferTransaction
from models.account import Account
from datetime import datetime

def test_account_transfer_transaction_valid_creation(db, mongodb,user):
    accounts = Account.objects(owner=user)
    from_account = accounts[0]
    to_account = accounts[1]
    amount = 200

    t = AccountsTransferTransaction(owner=user, amount=amount, to_account_id=to_account.id, from_account_id=from_account.id,
                                    time_accomplished=datetime.now())
    t.save()

    assert len(t.account_transactions) == 2
    assert sum([at.change for at in t.account_transactions]) == 0
    assert to_account in [at.account for at in t.account_transactions]
    assert from_account in [at.account for at in t.account_transactions]
    assert amount in [at.change for at in t.account_transactions]


