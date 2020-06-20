
from .fixtures import *
from decimal import Decimal
from utils import fund_utils
from models.fund import Fund

def test_fund_assigments_for_expense(db, mongodb, user):

    fund = Fund.objects(owner=user, is_default=False)[0]
    change = 2000

    transactions = fund_utils.create_assigments_for_expense(fund, change)

    assert len(transactions) == 1
    assert transactions[0].change == Decimal(change).quantize(Decimal("1.00"))
    assert transactions[0].fund == fund

