
from models.transaction import Transaction
from models.account_transaction import AccountTransaction
from models.fund_transaction import FundTransaction
from datetime import date
from .fixtures import *

def test_minus_transaction_retrieve_reverse_transaction(db, mongodb):
    transaction = Transaction(owner="60528afc743bfda62d489ff0",
                              date_accomplished=date.today(),
                              description="A description",
                              created_at=date.today(),
                              category="5ec742d8192cf1720a17037d"
                              )

    transaction.account_transactions.insert(0, AccountTransaction(account="5ec7441e192cf1720a170389", change=2000))
    transaction.account_transactions.insert(0, AccountTransaction(account="5ec7441e192cf1720a170382", change=-2000))

    transaction.fund_transactions.insert(0, FundTransaction(fund="5ec7441e192cf1720a170381", change=-500))

    transaction.fund_transactions.insert(0, FundTransaction(fund="5ec7441e192cf1720a170181", change=200))

    transaction.fund_transactions.insert(0, FundTransaction(fund="1ec7441e192cf1720a170181", change=400))

    reversed_transaction = -transaction

    assert transaction.owner == reversed_transaction.owner
    assert transaction.date_accomplished == reversed_transaction.date_accomplished
    assert transaction.description == reversed_transaction.description
    assert transaction.created_at == reversed_transaction.created_at
    assert transaction.category == reversed_transaction.category
    assert transaction.total_change == -reversed_transaction.total_change

    assert len(transaction.account_transactions) == len(reversed_transaction.account_transactions)
    assert len(transaction.fund_transactions) == len(reversed_transaction.fund_transactions)

    for i in range(0,len(transaction.fund_transactions)):
        assert transaction.fund_transactions[i].fund == reversed_transaction.fund_transactions[i].fund
        assert transaction.fund_transactions[i].change == -reversed_transaction.fund_transactions[i].change

    for i in range(0,len(transaction.account_transactions)):
        assert transaction.account_transactions[i].account == reversed_transaction.account_transactions[i].account
        assert transaction.account_transactions[i].change == -reversed_transaction.account_transactions[i].change


