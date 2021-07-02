from .test_transaction_resource import resource_url as transactions_url

resource_url = '/api/accounts'


def test_get_accounts_as_success(client, authenticated_header):
    rv = client.get(resource_url, headers=authenticated_header)
    assert rv.status_code == 200

    json_data = rv.get_json()
    assert type(json_data) is list
    assert len(json_data) > 0
    for e in json_data:
        assert 'id' in e
        assert 'name' in e
        assert 'balance' in e


def test_post_account_as_success(client, authenticated_header):
    rv = client.post(resource_url, headers=authenticated_header, json={'name': 'New Account'})
    assert rv.status_code == 200

    json_data = rv.get_json()
    assert 'id' in json_data


def test_post_account_invalid(client, authenticated_header):
    rv = client.post(resource_url, headers=authenticated_header, json={})
    assert rv.status_code == 400

    rv = client.post(resource_url, headers=authenticated_header, json={'name': ""})
    assert rv.status_code == 400


def test_account_unauthorized_request(client):
    rv = client.get(resource_url)
    assert rv.status_code == 401

    rv = client.post(resource_url, json={'name': 'New Account'})
    assert rv.status_code == 401


def test_account_with_initial_balance(client, authenticated_header):
    initial_balance = 2100
    rv = client.post(resource_url, headers=authenticated_header,
                     json={'name': 'New Account', 'initial_balance': initial_balance})
    assert rv.status_code == 200

    account_id = rv.get_json()['id']

    rv = client.get(transactions_url, query_string={'account_id': account_id}, headers=authenticated_header)

    items = rv.get_json()['_items']  # TODO extract from _items when pagination implemented

    assert len(items) == 1
    assert items[0]['account_transactions'][0]['account'] == account_id
