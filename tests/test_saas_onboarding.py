import os
import re
import uuid
import unittest
from datetime import timedelta

os.environ.setdefault('ALLOW_SQLITE_FALLBACK', 'true')
os.environ.setdefault('SECRET_KEY', 'saas-test-secret')

from app import app
from models.schema import Company, Subscription, User


class SaaSOnboardingTests(unittest.TestCase):
    def test_public_pages_and_registration_create_trial(self):
        client = app.test_client()
        self.assertEqual(client.get('/').status_code, 200)
        self.assertEqual(client.get('/register').status_code, 200)
        html = client.get('/register').get_data(as_text=True)
        token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
        email = f"saas-{uuid.uuid4().hex[:12]}@example.com"
        response = client.post('/register', data={
            'csrf_token': token, 'company_name': 'شركة اختبار',
            'owner_name': 'مسؤول الاختبار', 'phone': '0500000000',
            'email': email, 'password': 'StrongPass123',
            'password_confirmation': 'StrongPass123',
        })
        self.assertEqual(response.status_code, 302)
        with app.app_context():
            company = Company.query.filter_by(email=email).first()
            self.assertIsNotNone(company)
            self.assertEqual(company.status, 'trial')
            self.assertEqual((company.trial_ends_at - company.trial_started_at).days, 14)
            self.assertEqual(User.query.filter_by(company_id=company.id, role='admin').count(), 1)
            self.assertEqual(Subscription.query.filter_by(company_id=company.id, status='trial').count(), 1)


if __name__ == '__main__':
    unittest.main()
