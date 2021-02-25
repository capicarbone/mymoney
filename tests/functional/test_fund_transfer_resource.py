
from .fixtures import *

resource_url = '/api/transaction/fund-transfer'

def test_post_valid_fund_transfer(client, authenticated_header, mongodb):

    transfer_data = {
        'from': '5ec741e6192cf1720a170378',
        'to': '5ec741fc192cf1720a170379',
        'amount': 200
    }

    rv = client.post(resource_url, headers=authenticated_header, json=transfer_data)

    assert rv.status_code == 200

def test_post_invalid_fund_transfer(client, authenticated_header, mongodb):
    transfer_data = {
        'from': '5ec741e6192cf1720a170378',
        'to': '5ec741fc192cf1720a170379',
    }

    rv = client.post(resource_url, headers=authenticated_header, json=transfer_data)

    assert rv.status_code == 400

    transfer_data = {
        'to': '5ec741fc192cf1720a170379',
        'amount': 200
    }

    rv = client.post(resource_url, headers=authenticated_header, json=transfer_data)

    assert rv.status_code == 400

