import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("ALLOW_SQLITE_FALLBACK", "true")
os.environ.setdefault("SECRET_KEY", "local-add-user-audit")

from app import app

client = app.test_client()
with client.session_transaction() as sess:
    sess["authenticated"] = True
    sess["role"] = "admin"
    sess["user"] = "admin"

for password in ("Asd@123123K", "Asd@123123K!9"):
    response = client.post(
        "/api/users",
        json={
            "name": "محمد العتيبي",
            "username": "audit_probe_user",
            "email": "r.fhawas@example.com",
            "password": password,
        },
    )
    print(len(password), response.status_code, response.get_json(silent=True))
    if len(password) < 12:
        assert response.status_code == 400
        assert response.get_json()["error"] == "weak"
