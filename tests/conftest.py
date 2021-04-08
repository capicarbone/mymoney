
import pytest
from models.category import TransactionCategory
from models.account import Account
from models.fund import Fund

@pytest.fixture()
def main_user_id(mongodb):
    return "5ec7411b8741c3f6e1f07cea"

@pytest.fixture()
def income_category(mongodb):
    return TransactionCategory.objects(id='5f60d51cc22a5d685b27bfe4').get()

@pytest.fixture()
def accounts(main_user_id):
    return Account.objects(owner=main_user_id).all()

@pytest.fixture()
def funds(main_user_id):
    return Fund.objects(owner=main_user_id).all()

@pytest.fixture()
def expense_categories(main_user_id):
    return TransactionCategory.objects(owner=main_user_id, kind="expense").all()