import os
import re
import uuid
import unittest
from unittest.mock import patch

os.environ.setdefault('ALLOW_SQLITE_FALLBACK', 'true')
os.environ.setdefault('SECRET_KEY', 'saas-test-secret')

from app import app, db
from models.schema import Company, Driver, Subscription, User


def _csrf(client, path='/register'):
    html = client.get(path).get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def _register(client, email, company_name='شركة اختبار'):
    return client.post('/register', data={
        'csrf_token': _csrf(client), 'company_name': company_name,
        'owner_name': 'مسؤول الاختبار', 'phone': '0500000000',
        'email': email, 'password': 'StrongPass123',
        'password_confirmation': 'StrongPass123',
    })


class SaaSOnboardingTests(unittest.TestCase):
    def test_public_pages_and_registration_create_trial(self):
        client = app.test_client()
        self.assertEqual(client.get('/').status_code, 200)
        self.assertEqual(client.get('/register').status_code, 200)
        self.assertEqual(client.get('/saas-login').status_code, 200)
        email = f"saas-{uuid.uuid4().hex[:12]}@example.com"
        response = _register(client, email)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/workspace', response.headers.get('Location', ''))
        self.assertEqual(client.get('/workspace').status_code, 200)
        with app.app_context():
            company = Company.query.filter_by(email=email).first()
            self.assertIsNotNone(company)
            self.assertEqual(company.status, 'trial')
            self.assertEqual((company.trial_ends_at - company.trial_started_at).days, 14)
            self.assertEqual(User.query.filter_by(company_id=company.id, role='admin').count(), 1)
            self.assertEqual(Subscription.query.filter_by(company_id=company.id, status='trial').count(), 1)

    def test_duplicate_email_registration_shows_clear_error_not_500(self):
        client = app.test_client()
        email = f"dup-{uuid.uuid4().hex[:12]}@example.com"
        first = _register(client, email)
        self.assertEqual(first.status_code, 302)

        other_client = app.test_client()
        second = _register(other_client, email, company_name='شركة أخرى')
        self.assertEqual(second.status_code, 422)
        html = second.get_data(as_text=True)
        self.assertIn('يوجد حساب بهذا البريد مسبقًا', html)
        with app.app_context():
            self.assertEqual(Company.query.filter_by(email=email).count(), 1)
            self.assertEqual(User.query.filter(db.func.lower(User.email) == email).count(), 1)

    def test_registration_db_failure_is_handled_gracefully_and_rolls_back(self):
        client = app.test_client()
        email = f"txfail-{uuid.uuid4().hex[:12]}@example.com"
        with patch.object(db.session, 'commit', side_effect=Exception('simulated db failure')):
            response = _register(client, email)
        self.assertEqual(response.status_code, 422)
        self.assertNotIn('Traceback', response.get_data(as_text=True))
        with app.app_context():
            # A failed transaction must not leave a half-created company/user behind.
            self.assertIsNone(Company.query.filter_by(email=email).first())
            self.assertIsNone(User.query.filter(db.func.lower(User.email) == email).first())

    def test_company_session_cannot_see_another_companys_drivers_or_legacy_app(self):
        """Regression test for the cross-company data exposure fixed in this same audit
        pass: a self-registered company's own admin session must never reach the real
        legacy branch-scoped app (real driver/vehicle data) or another company's data."""
        with app.app_context():
            real_driver = Driver(branch_id=1, employee_id=f"T{uuid.uuid4().hex[:6]}",
                                  name='سائق بيانات حقيقية للاختبار', iqama_number=uuid.uuid4().hex[:10],
                                  phone='0500000001')
            db.session.add(real_driver)
            db.session.commit()

        client = app.test_client()
        email = f"isolation-{uuid.uuid4().hex[:12]}@example.com"
        response = _register(client, email)
        self.assertEqual(response.status_code, 302)

        # The full legacy single-company app, and /employees specifically (built on a
        # raw, unbranched table with no per-company isolation possible), must stay
        # fully blocked for a company session.
        for path in ('/dashboard', '/employees'):
            result = client.get(path)
            is_blocked = result.status_code == 403 or (
                result.status_code in (301, 302) and '/workspace' in result.headers.get('Location', '')
            )
            self.assertTrue(is_blocked, f"{path} was NOT blocked for a company session (status={result.status_code})")

        # /fleet_dashboard and /api/driver-vehicle-options WERE opened up as curated,
        # individually-verified-safe trial tabs (see app.py _SAAS_TRIAL_TAB_PATHS) —
        # they must be reachable, but must never surface the real driver seeded above.
        for path in ('/fleet_dashboard', '/api/driver-vehicle-options'):
            result = client.get(path)
            self.assertEqual(result.status_code, 200, f"{path} should be reachable for a trial company session")
            self.assertNotIn('سائق بيانات حقيقية للاختبار', result.get_data(as_text=True),
                              f"{path} leaked the real بن زومة driver to a company session")

        # The platform-admin panel (manages every company) must also stay out of reach.
        admin_result = client.get('/platform-admin')
        admin_blocked = admin_result.status_code == 403 or (
            admin_result.status_code in (301, 302) and '/workspace' in admin_result.headers.get('Location', '')
        )
        self.assertTrue(admin_blocked, f"/platform-admin was NOT blocked (status={admin_result.status_code})")

        # Its own workspace must still work normally.
        self.assertEqual(client.get('/workspace').status_code, 200)


if __name__ == '__main__':
    unittest.main()
