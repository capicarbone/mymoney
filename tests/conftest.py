
import pytest
from models.category import TransactionCategory
from models.account import Account

owner_id = "5ec7411b8741c3f6e1f07cea"

@pytest.fixture()
def income_category(mongodb):
    return TransactionCategory.objects(id='5f60d51cc22a5d685b27bfe4').get()

@pytest.fixture()
def accounts(mongodb):
    return Account.objects(owner=owner_id).all()

@pytest.fixture()
def expense_categories(mongodb):
    return TransactionCategory.objects(owner=owner_id, kind="expense").all()