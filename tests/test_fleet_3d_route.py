import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("ALLOW_SQLITE_FALLBACK", "true")
os.environ.setdefault("SECRET_KEY", "fleet-3d-route-test")

from app import app


class Fleet3DRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_page_requires_login(self):
        for path in ("/fleet-3d-control", "/fleet-3d-control/", "/fleet_3d"):
            response = self.client.get(path)
            self.assertIn(response.status_code, (301, 302))
            self.assertIn("/login", response.location)

    def test_authenticated_page_and_live_config(self):
        with self.client.session_transaction() as session:
            session["authenticated"] = True
            session["user"] = "fleet-3d-test"

        response = self.client.get("/fleet-3d-control")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("static/fleet3d/config.js", html)
        self.assertIn("/tracking", html)

        config = self.client.get("/static/fleet3d/config.js")
        self.assertEqual(config.status_code, 200)
        config_text = config.get_data(as_text=True)
        self.assertIn('apiUrl: "/api/gps"', config_text)
        self.assertIn("useMockOnError: false", config_text)


if __name__ == "__main__":
    unittest.main()
