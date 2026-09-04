import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('ALLOW_SQLITE_FALLBACK', 'true')
os.environ.setdefault('SECRET_KEY', 'local-test-secret')

from app import app

client = app.test_client()
with patch('routes.auth.User.query', side_effect=Exception('simulated missing reset columns')):
    response = client.get('/reset-password/not-a-valid-token')
    assert response.status_code == 400, response.status_code
    assert 'غير صالح' in response.get_data(as_text=True)
print('reset query failure smoke test: PASS')
