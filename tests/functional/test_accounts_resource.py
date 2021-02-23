
from .fixtures import *

def test_accounts_get(client, mongodb):
    rv = client.get('/api/accounts', headers={'Authorization': 'Bearer 4427db92-e12f-4dbd-a8d2-46bb3ad85afe'})
    assert rv.status_code == 200