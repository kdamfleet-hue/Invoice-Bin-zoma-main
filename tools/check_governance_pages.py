from pathlib import Path
from jinja2 import Environment, FileSystemLoader

root = Path(__file__).resolve().parents[1]
env = Environment(loader=FileSystemLoader(root / "templates"))
for name in ("data_quality.html", "audit_log.html"):
    env.parse((root / "templates" / name).read_text(encoding="utf-8"))
for name in ("data_quality.html", "audit_log.html", "driver_vehicle_assignments.html"):
    assert (root / "templates" / name).exists(), name
print("governance templates: OK")
