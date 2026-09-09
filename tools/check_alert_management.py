import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('ALLOW_SQLITE_FALLBACK', 'true')
os.environ.setdefault('SQLITE_PATH', '/tmp/invoice-alert-management-check.sqlite')
os.environ.setdefault('SECRET_KEY', 'local-alert-check')
os.environ.setdefault('TESTING', '1')

from app import app

client = app.test_client()

unauth = client.get('/api/alerts/manage')
assert unauth.status_code in (401, 302), unauth.status_code

with client.session_transaction() as sess:
    sess['authenticated'] = True
    sess['is_admin'] = True
    sess['role'] = 'admin'
    sess['user'] = 'local-admin'

page = client.get('/alerts')
assert page.status_code == 200, page.status_code
assert 'مركز إدارة التنبيهات والإجراءات' in page.get_data(as_text=True)

listing = client.get('/api/alerts/manage')
assert listing.status_code == 200, listing.status_code
payload = listing.get_json()
assert payload.get('success') is True
assert isinstance(payload.get('alerts'), list)

invalid = client.post('/api/alerts/manage', json={'action': 'complete'})
assert invalid.status_code == 400, invalid.status_code

print('ALERT_MANAGEMENT_OK', len(payload['alerts']))
