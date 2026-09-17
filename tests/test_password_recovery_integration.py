import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TEST_DB = Path(tempfile.gettempdir()) / "invoice_bin_password_recovery.sqlite"
try:
    TEST_DB.unlink()
except FileNotFoundError:
    pass
os.environ.setdefault("ALLOW_SQLITE_FALLBACK", "true")
os.environ.setdefault("SQLITE_PATH", str(TEST_DB))
os.environ.setdefault("SECRET_KEY", "password-recovery-test-secret")

import app  # noqa: E402
from models.schema import User  # noqa: E402
from werkzeug.security import check_password_hash, generate_password_hash  # noqa: E402


def csrf(client, path):
    response = client.get(path)
    token = re.search(r'name="csrf_token" value="([^"]+)"', response.get_data(as_text=True))
    if not token:
        raise AssertionError(f"CSRF token missing from {path}")
    return token.group(1)


class PasswordRecoveryIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.username = "recovery-integration-user"
        with app.app.app_context():
            existing = User.query.filter_by(username=self.username).first()
            if existing:
                app.db.session.delete(existing)
                app.db.session.commit()
            self.user = User(
                username=self.username,
                email="recovery-integration@example.com",
                password_hash=generate_password_hash("OldPassword123"),
                role="viewer",
                is_active=True,
            )
            app.db.session.add(self.user)
            app.db.session.commit()

    def tearDown(self):
        with app.app.app_context():
            user = User.query.filter_by(username=self.username).first()
            if user:
                app.db.session.delete(user)
                app.db.session.commit()

    def test_both_login_surfaces_link_to_recovery(self):
        internal = self.client.get("/login").get_data(as_text=True)
        saas = self.client.get("/saas-login").get_data(as_text=True)
        self.assertIn('/forgot-password', internal)
        self.assertIn('source=saas', saas)
        self.assertEqual(self.client.get("/forgot-password").status_code, 200)
        self.assertEqual(self.client.get("/forgot-password?source=saas").status_code, 200)

    def test_request_open_reset_and_consume_single_use_token(self):
        captured = {}

        def capture_email(user, reset_url):
            captured["url"] = reset_url
            return "sent"

        with patch("routes.auth._send_password_reset_email", side_effect=capture_email):
            response = self.client.post(
                "/forgot-password",
                data={"csrf_token": csrf(self.client, "/forgot-password"), "identifier": self.username},
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("إذا كان الحساب موجودًا", response.get_data(as_text=True))
        self.assertIn("url", captured)

        parsed = urlparse(captured["url"])
        token = parsed.path.rsplit("/", 1)[-1]
        self.assertGreaterEqual(len(token), 40)

        reset_page = self.client.get(f"/reset-password/{token}")
        self.assertEqual(reset_page.status_code, 200)
        new_password = "NewSecurePass123"
        response = self.client.post(
            f"/reset-password/{token}",
            data={
                "csrf_token": csrf(self.client, f"/reset-password/{token}"),
                "new_password": new_password,
                "confirm_password": new_password,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login?reset=success", response.headers["Location"])

        with app.app.app_context():
            user = User.query.filter_by(username=self.username).first()
            self.assertIsNone(user.password_reset_token_hash)
            self.assertIsNone(user.password_reset_expires_at)
            self.assertTrue(check_password_hash(user.password_hash, new_password))

        # The old password must fail, while the new password must authenticate.
        old_login = self.client.post(
            "/login",
            data={
                "csrf_token": csrf(self.client, "/login"),
                "username": self.username,
                "password": "OldPassword123",
            },
        )
        self.assertEqual(old_login.status_code, 200)
        self.assertIn("اسم المستخدم أو كلمة المرور غير صحيحة", old_login.get_data(as_text=True))

        new_login = self.client.post(
            "/login",
            data={
                "csrf_token": csrf(self.client, "/login"),
                "username": self.username,
                "password": new_password,
            },
        )
        self.assertEqual(new_login.status_code, 302)
        self.assertIn("/dashboard", new_login.headers["Location"])

        # The single-use token must no longer work.
        self.assertEqual(self.client.get(f"/reset-password/{token}").status_code, 400)

    def test_invalid_password_inputs_are_rejected_without_changing_password(self):
        captured = {}

        def capture_email(user, reset_url):
            captured["url"] = reset_url
            return "sent"

        with patch("routes.auth._send_password_reset_email", side_effect=capture_email):
            self.client.post(
                "/forgot-password",
                data={"csrf_token": csrf(self.client, "/forgot-password"), "identifier": self.username},
            )
        token = urlparse(captured["url"]).path.rsplit("/", 1)[-1]

        weak = self.client.post(
            f"/reset-password/{token}",
            data={
                "csrf_token": csrf(self.client, f"/reset-password/{token}"),
                "new_password": "weak",
                "confirm_password": "weak",
            },
        )
        self.assertEqual(weak.status_code, 200)
        self.assertIn("12 حرفًا على الأقل", weak.get_data(as_text=True))

        mismatch = self.client.post(
            f"/reset-password/{token}",
            data={
                "csrf_token": csrf(self.client, f"/reset-password/{token}"),
                "new_password": "AnotherSecure123",
                "confirm_password": "DifferentSecure123",
            },
        )
        self.assertEqual(mismatch.status_code, 200)
        self.assertIn("تأكيد كلمة المرور غير مطابق", mismatch.get_data(as_text=True))

        with app.app.app_context():
            user = User.query.filter_by(username=self.username).first()
            self.assertTrue(check_password_hash(user.password_hash, "OldPassword123"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
