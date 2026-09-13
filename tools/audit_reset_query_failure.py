import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('ALLOW_SQLITE_FALLBACK', 'true')
os.environ.setdefault('SECRET_KEY', 'local-test-secret')

from app import app
from models.schema import User


class FailingQuery:
    def filter_by(self, **kwargs):
        raise Exception('simulated missing reset columns')


client = app.test_client()
with app.app_context():
    with patch.object(User, 'query', new=FailingQuery()):
        response = client.get('/reset-password/' + ('A' * 43))
assert response.status_code == 400, response.status_code
assert 'غير صالح' in response.get_data(as_text=True)
print('reset query failure smoke test: PASS')
