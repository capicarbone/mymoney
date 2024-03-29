from decimal import Decimal

import pytest
import datetime

resource_url = '/api/reports/statements'


def reversed_months(start_month):
    """
    Generator for months order in reverse. User for check decrease order.
    :param start_month: month to start
    """
    current_month = start_month
    while True:
        yield current_month
        current_month = 12 - ((13 - current_month) % 12)


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


def is_valid_statement(entity):
    expected_fields = ['level', 'month', 'year', 'accounts', 'funds', 'categories']

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
def load_transactions(client,
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
    statements_count = 1

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
            res = client.post('/api/transactions',
                              headers=authenticated_header,
                              json=transaction_data)

            assert res.status_code == 200

        statements_count += 1 + int((current_month + 1) / 12)
        current_year += int((current_month + 1) / 12)
        current_month = (current_month + 1) % 12

    return statements_count


@pytest.fixture()
def transactions(client, authenticated_header, load_transactions):
    transactions = []
    page = 1

    while True:
        response = client.get('/api/transactions',
                              query_string={'page': page},
                              headers=authenticated_header)

        if response.status_code != 200:
            break

        data = response.get_json()
        items = data['_items']
        transactions.extend(items)

        page += 1

    return transactions


def test_transaction_post_creates_statements(client,
                                             authenticated_header,
                                             income_category,
                                             accounts):
    res = client.get(resource_url,
                     headers=authenticated_header)

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
                     headers=authenticated_header)

    assert res.status_code == 200

    assert type(res.get_json()['_items']) is list
    assert len(res.get_json()['_items']) == 3
    assert res.get_json()['_count'] == 3
    first_item = res.get_json()['_items'][0]
    assert is_valid_statement(first_item)


def test_pagination(client, authenticated_header, load_transactions):
    items_per_page = int(load_transactions / 4)

    res = client.get(resource_url,
                     headers=authenticated_header,
                     query_string={'page_size': items_per_page})

    assert res.status_code == 200
    data = res.get_json()
    assert type(data['_items']) is list
    assert data['_page'] == 1
    assert len(data['_items']) == items_per_page
    assert data['_count'] == load_transactions

    res = client.get(resource_url,
                     headers=authenticated_header,
                     query_string={'page_size': items_per_page,
                                   'page': 1})

    assert res.status_code == 200
    data = res.get_json()
    assert data['_page'] == 1
    assert len(data['_items']) == items_per_page
    assert data['_count'] == load_transactions


def test_order(client, authenticated_header, load_transactions):
    page = 1
    items = []
    while True:
        res = client.get(resource_url, headers=authenticated_header,
                         query_string={'page': page})

        data = res.get_json()
        items.extend(data['_items'])

        if len(items) == data['_count']:
            break

        page += 1

    assert items[0]['level'] == 1
    next_year = None
    start_year = None

    month_statement_start = 0
    for i in range(1, len(items)):
        item = items[i]

        if item['level'] != 2:
            month_statement_start = i
            break

        assert item['level'] == 2
        if next_year is None:
            next_year = item['year']
            start_year = next_year

        assert item['year'] == next_year
        next_year -= 1

    current_year = start_year
    month_generator = None

    for i in range(month_statement_start, len(items)):
        item = items[i]
        assert item['level'] == 3

        if month_generator is None:
            month_generator = reversed_months(item['month'])

        current_month = next(month_generator)
        assert item['month'] == current_month
        assert item['year'] == current_year

        if current_month == 1:
            current_year -= 1


def test_get_statements_returns_empty_list(client, authenticated_header):
    res = client.get(resource_url,
                     headers=authenticated_header,
                     query_string={'year': 2000}
                     )

    assert res.status_code == 200
    assert type(res.get_json()['_items']) is list
    assert len(res.get_json()['_items']) == 0
    assert res.get_json()['_count'] == 0


def test_transaction_delete_modifies_related_statements(client, authenticated_header, transactions):
    """
    This test currently only checks for changes on month statement (level 3). Checks on
    others levels is delegated to unit tests.
    """

    test_transaction = transactions[0]
    transaction_date = datetime.datetime.strptime(test_transaction['date_accomplished'], '%Y-%m-%dT%H:%M:%S')

    statement_initial_state = client.get(resource_url,
                                         headers=authenticated_header,
                                         query_string={'year': transaction_date.year,
                                                       'month': transaction_date.month}
                                         ).get_json()['_items'][0]

    client.delete('/api/transaction/%s' % (test_transaction['id']), headers=authenticated_header)

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

    test_category_id = test_transaction['category']
    category_change_initial_state = next(
        (Decimal(category_change['change']) for category_change in statement_initial_state['categories'] if
         category_change['category_id'] == test_category_id))

    category_change_next_state = next(
        (Decimal(category_change['change']) for category_change in statement_next_state['categories'] if
         category_change['category_id'] == test_category_id))

    assert statement_account_next_change == statement_account_initial_change - account_change
    assert statement_fund_next_change == statement_fund_initial_change - fund_change
    assert Decimal(category_change_next_state) == category_change_initial_state - account_change
