from pathlib import Path
from jinja2 import Environment, FileSystemLoader

root = Path(__file__).resolve().parents[1]
env = Environment(loader=FileSystemLoader(root / "templates"))
env.globals["url_for"] = lambda endpoint, **kwargs: "/static/" + kwargs.get("filename", "") if endpoint == "static" else "/"
env.globals["request"] = type("Request", (), {"path": "/driver-vehicle-assignments"})()
env.globals["get_flashed_messages"] = lambda **kwargs: []
env.globals["session"] = {}
template = env.get_template("driver_vehicle_assignments.html")
rows = [{"status":"active","driver_name":"سائق اختبار","employee_id":"T-1","driver_phone":"","plate":"أ ب ج 1234","vehicle_type":"نقل خفيف","model":"2024","serial_number":"TEST","received_date":"2026-01-01","returned_date":"","inspection_expiry":"2026-12-01","insurance_expiry":"2026-11-01","vehicle_id":1}]
rendered = template.render(rows=rows)
assert "سائق اختبار" in rendered
assert "أ ب ج 1234" in rendered
assert "قراءة فقط" in rendered
print("driver-vehicle assignment page: OK")
