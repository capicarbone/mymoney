
import mymoney
import pytest
import mongoengine

@pytest.fixture
def client(pytestconfig):
    # load testing config
    settings = {
        'MONGODB_SETTINGS': {
            'host': pytestconfig.getini('mongodb_host'),
            'retryWrites': False
        }
    }
    return mymoney.create_app(settings).test_client()