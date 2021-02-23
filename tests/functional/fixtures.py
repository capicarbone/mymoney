
from app import app
import pytest
import mongoengine

@pytest.fixture
def client():
    return app.test_client()