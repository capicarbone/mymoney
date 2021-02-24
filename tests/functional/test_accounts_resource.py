
from .fixtures import *

resource_url = '/api/accounts'

def test_get_accounts_as_success(client, authenticated_header, mongodb):
    rv = client.get(resource_url, headers=authenticated_header)
    assert rv.status_code == 200

    json_data = rv.get_json()
    assert type(json_data) is list
    assert len(json_data) > 0
    for e in json_data:
        assert 'id' in e
        assert 'name' in e
        assert 'balance' in e


def test_post_account_as_success(client, authenticated_header, mongodb):
    rv = client.post(resource_url, headers=authenticated_header, json={'name': 'New Account'})
    assert rv.status_code == 200

    json_data = rv.get_json()
    assert 'id' in json_data

def test_post_account_invalid(client, authenticated_header, mongodb):
    rv = client.post(resource_url, headers=authenticated_header, json={})
    assert rv.status_code == 400

    rv = client.post(resource_url, headers=authenticated_header, json={'name': ""})
    assert rv.status_code == 400

def test_account_unauthorized_request(client, mongodb):
    rv = client.get(resource_url)
    assert rv.status_code == 401

    rv = client.post(resource_url, json={'name': 'New Account'})
    assert rv.status_code == 401


