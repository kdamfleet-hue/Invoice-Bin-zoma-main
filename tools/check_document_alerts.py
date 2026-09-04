import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.document_alerts import build_message, configuration_status

status = configuration_status()
assert status["alerts_enabled"] is False
assert status["send_capable"] is False
message = build_message([{"name": "سائق اختبار", "plate": "أ ب ج 1234", "doc": "الرخصة", "date": "2026-09-20", "days": 16}])
assert "سائق اختبار" in message
assert "أ ب ج 1234" in message
assert "الرخصة" in message
print("document alerts: safe disabled-by-default mode OK")
