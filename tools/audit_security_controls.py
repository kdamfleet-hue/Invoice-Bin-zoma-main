import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("ALLOW_SQLITE_FALLBACK", "true")
os.environ.setdefault("SECRET_KEY", "local-security-audit")

from app import app

client = app.test_client()

# Cross-site state-changing requests must be rejected when an Origin is supplied.
csrf_probe = client.post(
    "/login",
    data={"username": "audit", "password": "invalid"},
    headers={"Origin": "https://evil.example"},
)
assert csrf_probe.status_code == 403, csrf_probe.status_code

# Sensitive pages are not public.
for path in ("/system_health", "/api/docs"):
    response = client.get(path)
    assert response.status_code in (302, 401), (path, response.status_code)

# CSP reports remain accepted and bounded.
assert client.post("/csp-report", json={"csp-report": {"blocked-uri": "https://example.invalid"}}).status_code == 204
assert client.post("/csp-report", data="x" * 9000, content_type="application/json").status_code == 413

print("security controls smoke test: PASS")
