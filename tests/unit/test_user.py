from .fixtures import *
from models.user import User
from models.fund import Fund
from werkzeug.security import generate_password_hash

def test_user_creation_with_default_fund(db, mongodb):
    user = User(name="Created user", email="testuser@savingsapp.com", password_hash=generate_password_hash("555555"))
    user.save()

    assert Fund.objects(owner=user, is_default=True).count() == 1