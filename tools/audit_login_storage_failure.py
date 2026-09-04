import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('ALLOW_SQLITE_FALLBACK', 'true')
os.environ.setdefault('SECRET_KEY', 'local-audit-secret')

from app import app

client = app.test_client()
with patch('app.get_branch_accounts', side_effect=RuntimeError('simulated storage failure')):
    response = client.post('/login', data={'username': 'audit-invalid-account', 'password': 'audit-invalid-password'})
    assert response.status_code == 200, response.status_code
    assert 'غير صحيحة' in response.get_data(as_text=True)
print('login storage failure smoke test: PASS')
