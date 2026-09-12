import os
import sys
import re
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
token = re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True)).group(1)

response = client.post('/forgot-password', data={'csrf_token': token, 'identifier': 'not-a-real-account'})
assert response.status_code == 200, response.status_code
assert 'إذا كان الحساب موجودًا' in response.get_data(as_text=True)

response = client.get('/reset-password/not-a-valid-token')
assert response.status_code == 400, response.status_code
assert 'غير صالح' in response.get_data(as_text=True)

print('password reset smoke tests: PASS')
