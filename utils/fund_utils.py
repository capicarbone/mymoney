
from datetime import datetime
from typing import List
from decimal import Decimal
from models.fund import Fund
from models.fund_transaction import FundTransaction

def create_assigments_for_expense(fund: Fund, total_change: Decimal) -> List[FundTransaction] :

    new_fund_transaction = FundTransaction(change=total_change,
                                           fund=fund)

    return [new_fund_transaction]

def create_assignments_for_income(funds:List[Fund], total_change: Decimal, from_time: datetime) -> List[FundTransaction]:

    fund_transactions = []
    default_fund: Fund = next((fund for fund in funds if fund.is_default))
    remaining = total_change
    total_adjustment = Decimal(0)

    funds_in_deficit = [fund for fund in funds if fund.get_deficit_from(from_time) > 0]

    total_deficit = sum([fund.get_deficit_from(from_time) for fund in funds_in_deficit])

    # Making assigment on funds with deficit, must be the priority
    for fund in funds_in_deficit:

        fund_balance = fund.balance_from(from_time)
        fund_deficit = fund.get_deficit_from(from_time)

        to_assign: Decimal = Decimal(total_change * fund.percentage_assigment)

        if total_deficit > total_change:
            to_assign = (total_change / len(funds_in_deficit)).quantize(Decimal('1.00'))
        else:
            if to_assign < fund_deficit:
                adjustment = fund_deficit - to_assign
                to_assign = to_assign + adjustment
                # We are going to use this for adjust on funds without deficit
                total_adjustment = total_adjustment + adjustment
            else:
                if fund.maximum_limit and to_assign + fund_balance > fund.maximum_limit:
                    to_assign = to_assign - ((to_assign + fund_balance) - fund.maximum_limit)

        to_assign = to_assign if to_assign <= remaining else remaining

        fund_transaction = FundTransaction(change=to_assign,
                                           fund=fund)

        fund_transactions.append(fund_transaction)

        remaining = remaining - to_assign

    assert 0 <= remaining <= total_change

    # Taking funds that does not have assigment yet
    funds_for_assignment = [fund for fund in funds if
                            not next((t for t in fund_transactions if t.fund == fund and not fund.is_default),
                                     None)]

    if remaining > 0:
        adjustment = total_adjustment / len(funds_for_assignment)
        for fund in funds_for_assignment:

            if fund.maximum_limit is not None and fund.balance >= fund.maximum_limit:
                continue

            to_assign = (total_change * fund.percentage_assigment) - adjustment

            if to_assign < 0.009:
                continue

            to_assign = to_assign if to_assign <= remaining else remaining

            f_transaction = FundTransaction(change=to_assign,
                                            fund=fund)
            fund_transactions.append(f_transaction)
            remaining = remaining - to_assign

    assert 0 <= remaining < total_change

    if remaining > 0:
        to_assign = total_change - sum([ft.change for ft in fund_transactions])
        fund_transaction = FundTransaction(change=to_assign,
                                           fund=default_fund)
        fund_transactions.append(fund_transaction)

    return fund_transactions