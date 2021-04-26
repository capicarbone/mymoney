from decimal import Decimal

import pytest
import datetime

resource_url = '/api/reports/month_statements'


def is_valid_account_change(account_change):
    expected_fields = ['account_id', 'income', 'expense']

    for field in expected_fields:
        assert field in account_change

    return True


def is_valid_fund_change(fund_change):
    expected_fields = ['fund_id', 'income', 'expense']

    for field in expected_fields:
        assert field in fund_change

    return True


def is_valid_category_change(category_change):
    expected_fields = ['category_id', 'change']

    for field in expected_fields:
        assert field in category_change

    return True


def is_valid_month_statement(entity):
    expected_fields = ['month', 'year', 'accounts', 'funds', 'categories']

    for field in expected_fields:
        assert field in entity

    assert type(entity['accounts']) is list
    assert type(entity['funds']) is list
    assert type(entity['categories']) is list

    assert is_valid_account_change(entity['accounts'][0])
    assert is_valid_fund_change(entity['funds'][0])
    assert is_valid_category_change(entity['categories'][0])

    return True


@pytest.fixture()
def load_month_transactions(client,
                            authenticated_header,
                            accounts,
                            income_category,
                            expense_categories):
    """

    :param client:
    :param authenticated_header:
    :param accounts:
    :param income_category:
    :param expense_categories:
    :return: Number of month statements created.
    """
    current_year = 2017
    current_month = 8
    end_year = 2020
    total_statements = 0

    while current_year <= end_year:
        transactions_data = []
        transactions_data.insert(0, {
            'change': 2000,
            'date_accomplished': '%d-%d-01' % (current_year, current_month + 1),
            'account_id': str(accounts[0].id),
            'category': str(income_category.id)
        })

        transactions_data.insert(0, {
            'change': -700,
            'date_accomplished': '%d-%d-01' % (current_year, current_month + 1),
            'account_id': str(accounts[0].id),
            'category': str(expense_categories[0].id)
        })

        transactions_data.insert(0, {
            'change': -900,
            'date_accomplished': '%d-%d-01' % (current_year, current_month + 1),
            'account_id': str(accounts[0].id),
            'category': str(expense_categories[1].id)
        })

        for transaction_data in transactions_data:
            # print(transaction_data)
            res = client.post('/api/transactions',
                              headers=authenticated_header,
                              json=transaction_data)

            assert res.status_code == 200

        current_year += int((current_month + 1) / 12)
        current_month = (current_month + 1) % 12

        total_statements += 1

    return total_statements


@pytest.fixture()
def transactions(client, authenticated_header, load_month_transactions):
    return client.get('/api/transactions', headers=authenticated_header).get_json()


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
    first_item = res.get_json()['_items'][0]
    assert is_valid_month_statement(first_item)
    assert first_item['year'] == query_params['year']
    assert first_item['month'] == query_params['month']


def test_get_month_statements_list_pagination(client, authenticated_header, load_month_transactions):
    items_per_page = int(load_month_transactions / 4)

    res = client.get(resource_url,
                     headers=authenticated_header,
                     query_string={'items_per_page': items_per_page})

    assert res.status_code == 200
    data = res.get_json()
    assert type(data['_items']) is list
    assert data['_page'] == 0
    assert len(data['_items']) == items_per_page
    assert data['_count'] == load_month_transactions

    res = client.get(resource_url,
                     headers=authenticated_header,
                     query_string={'items_per_page': items_per_page,
                                   'page': 1})

    assert res.status_code == 200
    data = res.get_json()
    assert data['_page'] == 1
    assert len(data['_items']) == items_per_page


def test_month_statement_returns_empty_list(client, authenticated_header):
    res = client.get(resource_url,
                     headers=authenticated_header,
                     query_string={'year': 2000}
                     )

    assert res.status_code == 200
    assert type(res.get_json()['_items']) is list
    assert len(res.get_json()['_items']) == 0
    assert res.get_json()['_count'] == 0


def test_transaction_delete_modifies_related_month_statement(client, authenticated_header, transactions):
    test_transaction = transactions[0]
    transaction_date = datetime.datetime.strptime(test_transaction['date_accomplished'], '%Y-%m-%dT%H:%M:%S')

    statement_initial_state = client.get(resource_url,
                                         headers=authenticated_header,
                                         query_string={'year': transaction_date.year,
                                                       'month': transaction_date.month}
                                         ).get_json()['_items'][0]

    t = client.delete('/api/transaction/%s' % (test_transaction['id']), headers=authenticated_header)

    statement_next_state = client.get(resource_url,
                                      headers=authenticated_header,
                                      query_string={'year': transaction_date.year,
                                                    'month': transaction_date.month}
                                      ).get_json()['_items'][0]

    account_id = test_transaction['account_transactions'][0]['account']
    account_change = Decimal(test_transaction['account_transactions'][0]['change'])
    fund_id = test_transaction['fund_transactions'][0]['fund']
    fund_change = Decimal(test_transaction['fund_transactions'][0]['change'])

    statement_account_initial_change = next(
        (Decimal(account['income']) + Decimal(account['expense']) for account in statement_initial_state['accounts'] if
         account['account_id'] == account_id))

    statement_account_next_change = next(
        (Decimal(account['income']) + Decimal(account['expense']) for account in statement_next_state['accounts'] if
         account['account_id'] == account_id))

    statement_fund_initial_change = next(
        (Decimal(fund['income']) + Decimal(fund['expense']) for fund in statement_initial_state['funds'] if
         fund['fund_id'] == fund_id))

    statement_fund_next_change = next(
        (Decimal(fund['income']) + Decimal(fund['expense']) for fund in statement_next_state['funds'] if
         fund['fund_id'] == fund_id))

    assert statement_account_next_change == statement_account_initial_change - account_change
    assert statement_fund_next_change == statement_fund_initial_change - fund_change
    assert Decimal(statement_next_state['categories'][0]['change']) == Decimal(
        statement_initial_state['categories'][0]['change']) - account_change
