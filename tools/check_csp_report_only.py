import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app

client = app.test_client()

for path in ("/login", "/api/docs", "/system_health"):
    response = client.get(path)
    policy = response.headers.get("Content-Security-Policy-Report-Only", "")
    assert policy, f"missing CSP Report-Only on {path}"
    assert "object-src 'none'" in policy
    assert "base-uri 'self'" in policy
    print(path, response.status_code, "CSP-Report-Only: present")

report = client.post("/csp-report", json={"csp-report": {"blocked-uri": "https://example.invalid"}})
assert report.status_code == 204, report.status_code
print("/csp-report", report.status_code, "accepted")

oversized = client.post("/csp-report", data="x" * 9000, content_type="application/json")
assert oversized.status_code == 413, oversized.status_code
print("/csp-report oversized", oversized.status_code, "rejected")
