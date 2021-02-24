
import pytest
from .fixtures import *

resource_url = '/api/transactions'

def test_successful_get_transaction(client, authenticated_header, mongodb):
    rv = client.get(resource_url, headers=authenticated_header)
    assert rv.status_code == 200

    json_data = rv.get_json()
    assert  type(json_data) is list

def test_successful_post_income_transaction(client, authenticated_header, mongodb):

    transaction_data = {
        'change': 2000,
        'date_accomplished': '2020-02-21',
        'account_id': '5ec7441e192cf1720a170389',
        'category': '5f60d51cc22a5d685b27bfe4'
    }

    rv = client.post(resource_url,
                     headers=authenticated_header,
                     json=transaction_data)

    assert rv.status_code == 200
    data = rv.get_json()
    assert  'id' in data
    assert 'account_transactions' in data
    assert len(data['account_transactions']) == 1

def test_successful_post_expense_transaction(client, authenticated_header, mongodb):
    transaction_data = {
        'change': -2000,
        'date_accomplished': '2020-02-21',
        'account_id': '5ec7441e192cf1720a170389',
        'category': '5ec742d8192cf1720a17037d'
    }

    rv = client.post(resource_url,
                     headers=authenticated_header,
                     json=transaction_data)

    assert rv.status_code == 200
    data = rv.get_json()
    assert 'id' in data
    assert 'account_transactions' in data
    assert len(data['account_transactions']) == 1

def test_invalid_post_transaction(client, authenticated_header, mongodb):
    transaction_data = {
        'date_accomplished': '2020-02-21',
        'account_id': '5ec7441e192cf1720a170389',
        'category': '5f60d51cc22a5d685b27bfe4'
    }

    rv = client.post(resource_url,
                     headers=authenticated_header,
                     json=transaction_data)

    assert rv.status_code == 400

    transaction_data = {
        'change': 2000,
        'account_id': '5ec7441e192cf1720a170389',
        'category': '5f60d51cc22a5d685b27bfe4'
    }

    rv = client.post(resource_url,
                     headers=authenticated_header,
                     json=transaction_data)

    assert rv.status_code == 400

    transaction_data = {
        'change': 2000,
        'date_accomplished': '2020-02-21',
        'category': '5f60d51cc22a5d685b27bfe4'
    }

    rv = client.post(resource_url,
                     headers=authenticated_header,
                     json=transaction_data)

    assert rv.status_code == 400

    transaction_data = {
        'change': 2000,
        'date_accomplished': '2020-02-21',
        'account_id': '5ec7441e192cf1720a170389'
    }

    rv = client.post(resource_url,
                     headers=authenticated_header,
                     json=transaction_data)

    assert rv.status_code == 400

def test_not_authenticated_get_transaction(client, mongodb):
    rv = client.get(resource_url)
    assert rv.status_code == 401
