
from .fixtures import *

resource_url = '/api/reports/month_statements'

def test_transaction_post_creates_month_statement(client, authenticated_header, mongodb):

    query_params = {'year': '2020', 'month': '2'}

    rv = client.get(resource_url,
                    headers=authenticated_header,
                    query_string=query_params)

    assert rv.status_code == 200
    assert type(rv.get_json()['_items']) is list
    assert len(rv.get_json()['_items']) == 0


    transaction_data = {
        'change': 2000,
        'date_accomplished': '2020-02-21',
        'account_id': '5ec7441e192cf1720a170389',
        'category': '5f60d51cc22a5d685b27bfe4'
    }

    client.post('/api/transactions',
                 headers=authenticated_header,
                 json=transaction_data)

    rv = client.get(resource_url,
                    headers=authenticated_header,
                    query_string=query_params)

    assert rv.status_code == 200
    assert type(rv.get_json()['_items']) is list
    assert len(rv.get_json()['_items']) == 1
