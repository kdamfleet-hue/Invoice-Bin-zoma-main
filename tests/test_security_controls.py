import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("ALLOW_SQLITE_FALLBACK", "true")
os.environ.setdefault("SECRET_KEY", "local-security-controls-test")

from app import app, db
from models.schema import User


class SecurityControlTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_csrf_required_for_state_changing_api(self):
        with self.client.session_transaction() as session:
            session.update({
                "authenticated": True,
                "role": "admin",
                "is_admin": True,
                "user": "admin",
                "_csrf_token": "csrf-test",
            })
        self.assertEqual(self.client.post("/api/users", json={}).status_code, 403)
        response = self.client.post(
            "/api/users", headers={"X-CSRFToken": "csrf-test"}, json={}
        )
        self.assertEqual(response.status_code, 400)

    def test_authorization_version_invalidates_session(self):
        with app.app_context():
            user = User.query.filter_by(is_active=True).first()
            if user is None:
                self.skipTest("no active database user available")
            old_version = int(user.authz_version or 1)
            with self.client.session_transaction() as session:
                session.clear()
                session.update({
                    "authenticated": True,
                    "user_id": user.id,
                    "username": user.username,
                    "user": user.username,
                    "role": user.role,
                    "authz_version": old_version,
                    "_csrf_token": "csrf-test",
                })
            user.authz_version = old_version + 1
            db.session.commit()
            try:
                response = self.client.get("/api/my_permissions")
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.get_json()["code"], "AUTHZ_CHANGED")
            finally:
                user.authz_version = old_version
                db.session.commit()


if __name__ == "__main__":
    unittest.main()
