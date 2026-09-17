import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Keep this integration test isolated from the developer's local database.
TEST_DB = Path(tempfile.gettempdir()) / "invoice_bin_manager_tasks_integration.sqlite"
try:
    TEST_DB.unlink()
except FileNotFoundError:
    pass
os.environ.setdefault("ALLOW_SQLITE_FALLBACK", "true")
os.environ.setdefault("SQLITE_PATH", str(TEST_DB))
os.environ.setdefault("SECRET_KEY", "integration-test-secret")
os.environ.setdefault("ADMIN_USERNAME", "integration-admin")
os.environ.setdefault("MASTER_PASSWORD", "integration-test-password")

import app  # noqa: E402


class ManagerTasksAuthorizationIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def set_session(self, **values):
        with self.client.session_transaction() as session:
            session.clear()
            session.update({"authenticated": True, **values})

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.get("/manager-tasks")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_admin_can_open_page_and_sees_sidebar_link(self):
        self.set_session(is_admin=True, role="admin")
        response = self.client.get("/manager-tasks")
        self.assertEqual(response.status_code, 200)
        self.assertIn("مهام المسؤول".encode(), response.data)
        self.assertIn(b'href="/manager-tasks"', response.data)

    def test_branch_manager_can_open_page_and_sees_sidebar_link(self):
        self.set_session(is_admin=False, role="branch_manager")
        response = self.client.get("/manager-tasks")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'href="/manager-tasks"', response.data)

    def test_operations_role_from_nested_user_is_normalized(self):
        self.set_session(is_admin=False, user={"role": " Operations "})
        response = self.client.get("/manager-tasks")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'href="/manager-tasks"', response.data)

    def test_structured_user_identity_does_not_trigger_permission_warning(self):
        self.set_session(
            is_admin=False,
            user={"username": "employee-1", "role": "operations"},
        )
        with self.assertNoLogs("InvoiceApp", level="WARNING"):
            response = self.client.get("/manager-tasks")
        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_open_manager_page_or_see_manager_link(self):
        self.set_session(is_admin=False, role="employee", user={"role": "employee"})
        response = self.client.get("/manager-tasks")
        self.assertEqual(response.status_code, 403)
        with app.app.test_request_context("/"):
            from flask import render_template
            from flask import session
            session.update({"authenticated": True, "role": "employee", "user": {"role": "employee"}})
            html = render_template("base.html", is_admin=False, active_branch="اختبار")
            self.assertNotIn('href="/manager-tasks"', html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
