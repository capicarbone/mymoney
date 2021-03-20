
import mymoney
import pytest
import mongoengine

from models.user import User

@pytest.fixture(scope="session")
def client(pytestconfig):
    # load testing config
    settings = {
        'MONGODB_SETTINGS': {
            'host': pytestconfig.getini('mongodb_host'),
            'retryWrites': False
        },
        'TESTING': True
    }
    return mymoney.create_app(settings).test_client()


@pytest.fixture()
def authenticated_header(mongodb):
    user = User.objects.first()
    return {'Authorization': 'Bearer %s' % (user.auth_token)}