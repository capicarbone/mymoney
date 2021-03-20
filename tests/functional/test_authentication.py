import base64
from .fixtures import *


def test_valid_login(client):
    credentials_base64 = base64.urlsafe_b64encode(b"cpinelly@gmail.com:555555")

    header = {'Authorization': 'Basic %s' % credentials_base64.decode("utf-8")}

    rv = client.post('/api/login', headers=header)

    assert rv.status_code == 200
    assert type(rv.get_json()) is dict
    assert 'token' in rv.get_json()


def test_invalid_login(client):
    credentials_base64 = base64.urlsafe_b64encode(b"c@gmail.com:555555")

    header = {'Authorization': 'Basic %s' % credentials_base64.decode("utf-8")}

    rv = client.post('/api/login', headers=header)

    assert rv.status_code == 401

    credentials_base64 = base64.urlsafe_b64encode(b"cpinelly@gmail.com:2323")

    header = {'Authorization': 'Basic %s' % credentials_base64.decode("utf-8")}

    rv = client.post('/api/login', headers=header)

    assert rv.status_code == 401
