
import mymoney
import pytest
import mongoengine
from models.user import User

@pytest.fixture(scope="module")
def client(pytestconfig):
    # load testing config
    settings = {
        'MONGODB_SETTINGS': {
            'host': pytestconfig.getini('mongodb_host'),
            'retryWrites': False
        },
        'TESTING': True
    }
    yield mymoney.create_app(settings).test_client()
    mongoengine.disconnect()


@pytest.fixture()
def authenticated_header(mongodb):
    user = User.objects.first()
    return {'Authorization': 'Bearer %s' % (user.auth_token)}