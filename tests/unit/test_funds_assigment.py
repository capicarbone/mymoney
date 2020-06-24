
from .fixtures import *
import pytest
from decimal import Decimal
from utils import fund_utils
from models.fund import Fund
from models.account import Account
from models.income_transaction import IncomeTransaction
import datetime

def test_fund_assignments_for_expense(db, mongodb, user):

    fund = Fund.objects(owner=user, is_default=False)[0]
    change = -2000

    transactions = fund_utils.create_assigments_for_expense(fund, change)

    assert len(transactions) == 1
    assert transactions[0].change == Decimal(change).quantize(Decimal("1.00"))
    assert transactions[0].fund == fund

@pytest.mark.parametrize(('change', 'expected_assignments'), [
    (0.01, {
        'Unassigned': Decimal(0.01).quantize(Decimal("0.01"))
    }),
    (0.3, {
        "Home": Decimal(0.1).quantize(Decimal("1.00")),
        "Family": Decimal(0.1).quantize(Decimal("1.00")),
        "Health": Decimal(0.1).quantize(Decimal("1.00"))
    }),
    (0.4, {
        "Home": Decimal(0.13).quantize(Decimal("1.00")),
        "Family": Decimal(0.13).quantize(Decimal("1.00")),
        "Health": Decimal(0.13).quantize(Decimal("1.00")),
        'Unassigned': Decimal(0.01).quantize(Decimal("1.00"))
    }),
    (5, {
        "Home": Decimal(1.67).quantize(Decimal("1.00")),
        "Family": Decimal(1.67).quantize(Decimal("1.00")),
        "Health": Decimal(1.66).quantize(Decimal("1.00"))
    }),
    (23, {
        "Home": Decimal(7.67).quantize(Decimal("1.00")),
        "Family": Decimal(7.67).quantize(Decimal("1.00")),
        "Health": Decimal(7.66).quantize(Decimal("1.00"))
    }),
    (2100, {
        "Home": Decimal(700).quantize(Decimal("1.00")),
        "Family": Decimal(700).quantize(Decimal("1.00")),
        "Health": Decimal(700).quantize(Decimal("1.00"))
    }),
    (1000, {
        "Home": Decimal(333.33).quantize(Decimal("1.00")),
        "Family": Decimal(333.33).quantize(Decimal("1.00")),
        "Health": Decimal(333.33).quantize(Decimal("1.00")),
        'Unassigned': Decimal(0.01).quantize(Decimal("1.00"))
    }),
    (10000, {
        "Home": Decimal(3333.33).quantize(Decimal("1.00")),
        "Family": Decimal(3333.33).quantize(Decimal("1.00")),
        "Health": Decimal(3333.33).quantize(Decimal("1.00")),
        'Unassigned': Decimal(0.01).quantize(Decimal("1.00"))
    })
])
def test_fund_assignments_for_income_with_funds_on_deficit_and_change_is_not_enough_for_total_deficit(db, mongodb, change, expected_assignments):
    """
    The test is rand with a user witout any transaction and funds on deficit.
    :param db:
    :param mongodb:
    :return:
    """

    funds = Fund.objects(owner="5ee24ef16c8e3ad070cbf919")
    change = Decimal(change)

    transactions = fund_utils.create_assignments_for_income(funds, change, datetime.datetime.now())

    assert len(transactions) == len(funds)

    # The number of assigned fund is equals to the funds with minimum_limit
    funds_assigned = [transaction for transaction in transactions if transaction.change > 0]
    funds_in_deficit = [fund for fund in funds if fund.minimum_limit is not None]
    assert len(funds_assigned) == len(expected_assignments)

    for assignment in funds_assigned:
        fund = assignment.fund.fetch()
        assert assignment.change == expected_assignments[fund.name], "Fund {} with not expected assignment".format(fund.name)

    assert sum([t.change for t in funds_assigned]) == Decimal(change).quantize(Decimal("1.00"))

@pytest.mark.parametrize(('change', 'expected_assignments'), [
    (8000, {
        "Home": Decimal(2666.67).quantize(Decimal("1.00")),
        "Family": Decimal(2000).quantize(Decimal("1.00")),
        "Health": Decimal(2666.67).quantize(Decimal("1.00")),
        'Unassigned': Decimal(666.66).quantize(Decimal("1.00"))
    }),
    (12000, {
        "Home": Decimal(3000).quantize(Decimal("1.00")),
        "Family": Decimal(3000).quantize(Decimal("1.00")),
        "Health": Decimal(2666.67).quantize(Decimal("1.00")),
        "Travel": Decimal(711.11).quantize(Decimal("1.00")),
        "Education": Decimal(711.11).quantize(Decimal("1.00")),
        'Unassigned': Decimal(1911.11).quantize(Decimal("1.00"))
    }),

])
def test_fund_assignments_for_income_with_funds_on_deficit_and_change_is_grather_than_total_deficit(db, mongodb, change, expected_assignments):

    owner_id="5ee24ef16c8e3ad070cbf919"
    account = Account.objects(owner=owner_id, name="Banco").get()
    income = IncomeTransaction(owner=owner_id, account_id=account, change=7000, time_accomplished=datetime.datetime.now())
    income.save()

    funds = Fund.objects(owner=owner_id)
    change = Decimal(change)

    transactions = fund_utils.create_assignments_for_income(funds, change, datetime.datetime.now())

    funds_assigned = [transaction for transaction in transactions if transaction.change > 0]

    assert len(funds_assigned) == len(expected_assignments)

    for assignment in funds_assigned:
        fund = assignment.fund.fetch()
        assert assignment.change == expected_assignments[fund.name], "Fund {} with not expected assignment".format(fund.name)

    assert sum([t.change for t in funds_assigned]) == Decimal(change).quantize(Decimal("1.00"))

