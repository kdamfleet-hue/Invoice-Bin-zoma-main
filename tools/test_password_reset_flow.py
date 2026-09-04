import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('ALLOW_SQLITE_FALLBACK', 'true')
os.environ.setdefault('SECRET_KEY', 'local-test-secret')

from app import app

client = app.test_client()

response = client.get('/login')
assert response.status_code == 200, response.status_code
assert 'نسيت كلمة المرور' in response.get_data(as_text=True)

response = client.get('/forgot-password')
assert response.status_code == 200, response.status_code

response = client.post('/forgot-password', data={'identifier': 'not-a-real-account'})
assert response.status_code == 200, response.status_code
assert 'إذا كان الحساب موجودًا' in response.get_data(as_text=True)

response = client.get('/reset-password/not-a-valid-token')
assert response.status_code == 400, response.status_code
assert 'غير صالح' in response.get_data(as_text=True)

print('password reset smoke tests: PASS')
