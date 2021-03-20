
from .fixtures import *

resource_url = '/api/transactions/categories'

def test_succesful_get_categories(client, authenticated_header):
    rv = client.get(resource_url, headers=authenticated_header)

    json_data = rv.get_json()
    assert type(json_data) is list
    assert len(json_data) > 0
    for e in json_data:
        assert 'id' in e
        assert 'name' in e


def test_succesful_post_category(client, authenticated_header):

    category_data = {
        'name': 'New category',
        'kind': 'income'
    }

    rv = client.post(resource_url, headers=authenticated_header, json=category_data)

    assert rv.status_code == 200
    assert 'id' in rv.get_json()

    category_data = {
        'name': 'New category',
        'kind': 'expense',
        'fund': '5ec741e6192cf1720a170378'
    }

    rv = client.post(resource_url, headers=authenticated_header, json=category_data)

    assert rv.status_code == 200
    assert 'id' in rv.get_json()

def test_invalid_post_category(client, authenticated_header):
    category_data = {
        'kind': 'income'
    }

    rv = client.post(resource_url, headers=authenticated_header, json=category_data)

    assert rv.status_code == 400

    category_data = {
        'name': 'New category',
        'kind': 'expense'
    }

    rv = client.post(resource_url, headers=authenticated_header, json=category_data)

    assert rv.status_code == 400

# TODO: Test for not authenticated request
# TODO: GET with fund_id parameter