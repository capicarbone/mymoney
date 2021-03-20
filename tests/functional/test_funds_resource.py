
resource_url = '/api/funds'


def test_succesful_fund_get(client, authenticated_header):
    rv = client.get(resource_url, headers=authenticated_header)
    assert rv.status_code == 200

    json_data = rv.get_json()
    assert type(json_data) is list
    assert len(json_data) > 0
    for e in json_data:
        assert 'id' in e
        assert 'name' in e
        assert 'percentage_assignment' in e
        assert 'balance' in e


def test_succesful_fund_post(client, authenticated_header):
    fund_data = {
        'name': 'New Fund',
        'percentage_assignment': 0.1,
        'description': 'A description',
        'minimum_limit': 300,
        'maximum_limit': 600
    }

    rv = client.post(resource_url, headers=authenticated_header, json=fund_data)

    assert rv.status_code == 200
    assert 'id' in rv.get_json()


def test_invalid_fund_post(client, authenticated_header):
    fund_data = {
        'percentage_assignment': 0.1,
        'description': 'A description',
    }

    rv = client.post(resource_url, headers=authenticated_header, json=fund_data)
    assert rv.status_code == 400

    fund_data = {
        'name': 'New Fund',
        'description': 'A description',
    }

    rv = client.post(resource_url, headers=authenticated_header, json=fund_data)
    assert rv.status_code == 400

    fund_data = {
        'name': 'New Fund',
        'percentage_assignment': 0.1,
        'description': 'A description',
        'minimum_limit': 600,
        'maximum_limit': 300
    }

    rv = client.post(resource_url, headers=authenticated_header, json=fund_data)
    assert rv.status_code == 400
