
from .fixtures import *

def test_accounts_get(client, mongodb):
    rv = client.get('/api/accounts', headers={'Authorization': 'Bearer fb3918e0-6e05-4c55-bbac-3c41ac3e0d4e'})
    assert rv.status_code == 200