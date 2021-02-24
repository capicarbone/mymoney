
from .fixtures import *

resource_url = '/api/transaction/account-transfer'

def test_successful_post_account_transfer(client, authenticated_header, mongodb):
    transfer_data = {
        'from': '5ec7441e192cf1720a170389',
        'to': '5ec74423192cf1720a17038a',
        'amount': 20,
        'date_accomplished': '2020-02-02'
    }

    rv = client.post(resource_url, headers=authenticated_header, json=transfer_data)

    assert rv.status_code == 200
    assert type(rv.get_json()) is dict
    assert 'id' in rv.get_json()


def test_invalid_post_account_transfer(client, authenticated_header, mongodb):
    transfer_data = {
        'from': '5ec7441e192cf1720a170389',
        'to': '5ec74423192cf1720a17038a',
        'date_accomplished': '2020-02-02'
    }

    rv = client.post(resource_url, headers=authenticated_header, json=transfer_data)

    assert rv.status_code == 400

    transfer_data = {
        'from': '5ec7441e192cf1720a170389',
        'amount': 20,
        'date_accomplished': '2020-02-02'
    }

    rv = client.post(resource_url, headers=authenticated_header, json=transfer_data)

    assert rv.status_code == 400

    transfer_data = {
        'to': '5ec74423192cf1720a17038a',
        'amount': 20,
        'date_accomplished': '2020-02-02'
    }

    rv = client.post(resource_url, headers=authenticated_header, json=transfer_data)

    assert rv.status_code == 400

    transfer_data = {
        'from': '5ec7441e192cf1720a170389',
        'to': '5ec74423192cf1720a17038a',
        'amount': 20,
    }

    rv = client.post(resource_url, headers=authenticated_header, json=transfer_data)

    assert rv.status_code == 400

def test_unauthoeized_post_account_transfer(client, mongodb):
    transfer_data = {
        'from': '5ec7441e192cf1720a170389',
        'to': '5ec74423192cf1720a17038a',
        'amount': 20,
        'date_accomplished': '2020-02-02'
    }

    rv = client.post(resource_url, json=transfer_data)

    assert rv.status_code == 401
