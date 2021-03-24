
import pytest

resource_url = '/api/reports/month_statements'

@pytest.fixture()
def loaded_month_transactions(client,
                              authenticated_header,
                              accounts,
                              income_category,
                              expense_categories):
    return None

def test_transaction_post_creates_month_statement(client,
                                                  authenticated_header,
                                                  income_category,
                                                  accounts):

    query_params = {'year': 2020, 'month': 2}

    res = client.get(resource_url,
                    headers=authenticated_header,
                    query_string=query_params)

    assert res.status_code == 200
    assert type(res.get_json()['_items']) is list
    assert res.get_json()['_count'] == 0


    transaction_data = {
        'change': 2000,
        'date_accomplished': '2020-02-21',
        'account_id': str(accounts[0].id),
        'category': str(income_category.id)
    }

    client.post('/api/transactions',
                 headers=authenticated_header,
                 json=transaction_data)

    res = client.get(resource_url,
                    headers=authenticated_header,
                    query_string=query_params)

    assert res.status_code == 200
    assert type(res.get_json()['_items']) is list
    assert len(res.get_json()['_items']) == 1
    assert res.get_json()['_count'] == 1
    assert res.get_json()['_items'][0]['year'] == query_params['year']
    assert res.get_json()['_items'][0]['month'] == query_params['month']

def test_get_month_statements_list_pagination(client, authenticated_header, loaded_month_transactions):
    assert True == True

def test_month_statement_returns_empty_list(client, authenticated_header):
    res = client.get(resource_url,
                     headers=authenticated_header,
                     query_string={'year': 2000}
                     )

    assert res.status_code == 200
    assert type(res.get_json()['_items']) is list
    assert len(res.get_json()['_items']) == 0

# TODO: Test paginattion, request just a year.
