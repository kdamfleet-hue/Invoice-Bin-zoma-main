import os
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import timedelta
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DB = Path(tempfile.gettempdir()) / "invoice_bin_company_platform_entry.sqlite"
DB.unlink(missing_ok=True)
os.environ.setdefault("ALLOW_SQLITE_FALLBACK", "true")
os.environ.setdefault("SQLITE_PATH", str(DB))
os.environ.setdefault("SECRET_KEY", "company-platform-entry-test")

import app  # noqa: E402
from models.schema import Company, User  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402


class CompanyPlatformEntryTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        suffix = uuid4().hex[:10]
        self.username = f"platform-entry-{suffix}@example.com"
        with app.app.app_context():
            company = Company(
                name=f"شركة اختبار المنصة {suffix}",
                owner_name="مسؤول الاختبار",
                phone="0500000000",
                email=self.username,
                trial_ends_at=app.utcnow() + timedelta(days=14),
            )
            app.db.session.add(company)
            app.db.session.flush()
            user = User(
                company_id=company.id,
                username=self.username,
                email=self.username,
                password_hash=generate_password_hash("StrongPass123"),
                role="admin",
                is_active=True,
            )
            app.db.session.add(user)
            app.db.session.commit()
            self.company_id = company.id

    def tearDown(self):
        with app.app.app_context():
            company = app.db.session.get(Company, self.company_id)
            if company:
                app.db.session.delete(company)
                app.db.session.commit()

    def test_km_login_page_surfaces_legacy_bin_zomah_portal(self):
        landing = self.client.get("/").get_data(as_text=True)
        saas_login = self.client.get("/saas-login").get_data(as_text=True)
        self.assertIn('href="/login"', landing)
        self.assertIn("بوابة بن زومة", landing)
        self.assertIn('href="/login"', saas_login)
        self.assertIn("الدخول إلى بوابة بن زومة", saas_login)

    def test_unauthenticated_entry_goes_to_company_login(self):
        response = self.client.get("/company-platform")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/saas-login", response.headers["Location"])

    def test_company_session_can_open_platform_entry(self):
        with self.client.session_transaction() as session:
            session.update({"authenticated": True, "company_id": self.company_id, "role": "admin"})
        response = self.client.get("/company-platform")
        self.assertEqual(response.status_code, 200)
        self.assertIn("تم فتح المنصة بنجاح", response.get_data(as_text=True))

    def test_workspace_button_uses_safe_company_platform_route(self):
        with self.client.session_transaction() as session:
            session.update({"authenticated": True, "company_id": self.company_id, "role": "admin"})
        response = self.client.get("/workspace")
        self.assertEqual(response.status_code, 200)
        self.assertIn('href="/company-platform"', response.get_data(as_text=True))

    def test_company_session_dashboard_redirects_to_workspace_without_loop(self):
        with self.client.session_transaction() as session:
            session.update({"authenticated": True, "company_id": self.company_id, "role": "admin"})
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/workspace", response.headers["Location"])
        follow = self.client.get(response.headers["Location"])
        self.assertEqual(follow.status_code, 200)

    def test_internal_session_can_open_dashboard(self):
        with app.app.app_context():
            internal = User(
                username=self.username + ".internal",
                email=self.username + ".internal",
                password_hash=generate_password_hash("StrongPass123"),
                role="admin",
                is_active=True,
            )
            app.db.session.add(internal)
            app.db.session.commit()
            internal_id = internal.id
        with self.client.session_transaction() as session:
            session.update({
                "authenticated": True,
                "user_id": internal_id,
                "username": internal.username,
                "user": internal.username,
                "role": "admin",
                "is_admin": True,
                "authz_version": 1,
            })
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
