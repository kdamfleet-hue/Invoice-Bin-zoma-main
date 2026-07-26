from app import app
from models.schema import db, User

with app.app_context():
    admin = User.query.filter_by(username='admin').first()

client = app.test_client()
with client.session_transaction() as sess:
    sess['authenticated'] = True
    sess['role'] = 'admin'
    sess['username'] = 'admin'
    sess['is_admin'] = True

try:
    response = client.get('/api/gps')
    print("GPS Response Status:", response.status_code)
except Exception as e:
    print("GPS Error:", repr(e))

try:
    response = client.get('/api/alert_settings')
    print("Alert Settings Response Status:", response.status_code)
except Exception as e:
    print("Alert Settings Error:", repr(e))
