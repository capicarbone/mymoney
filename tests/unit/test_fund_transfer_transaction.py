
from .fixtures import *
from models.fund import Fund
from models.fund_transfer_transaction import FundTransferTransaction
from datetime import datetime

def test_fund_transfer_transaction_valid_creation(db, mongodb,user):
    funds = Fund.objects(owner=user)
    to_fund = funds[0]
    from_fund = funds[0]
    amount = 300

    transfer = FundTransferTransaction(amount=amount, to_fund_id=to_fund.id, from_fund_id=from_fund, time_accomplished=datetime.now())
    transfer.save()

    assert len(transfer.fund_transactions) == 2
    assert sum([t.change for t in transfer.fund_transactions]) == 0
    assert next((t.change for t in transfer.fund_transactions if t.change == amount), None) is not None



