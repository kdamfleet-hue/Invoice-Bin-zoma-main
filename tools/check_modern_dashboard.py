from pathlib import Path
from jinja2 import Environment, FileSystemLoader

root = Path(__file__).resolve().parents[1]
env = Environment(loader=FileSystemLoader(root / "templates"))
env.globals["url_for"] = lambda endpoint, **kwargs: "/static/" + kwargs.get("filename", "") if endpoint == "static" else "/"
env.globals["request"] = type("Request", (), {"path": "/fleet_dashboard"})()
env.globals["get_flashed_messages"] = lambda **kwargs: []
env.globals["session"] = {}
template = env.get_template("fleet_dashboard_new.html")
rendered = template.render(insights={
    "fleet": {"drivers": 2, "with_vehicle": 1, "without_vehicle": 1, "vehicles": 1},
    "volume": {"employees": 2, "workshop": 3, "oils": 4, "purchase": 5, "gps_devices": 6},
    "score": {"value": 90, "label": "ممتاز"},
    "documents": {"expired": 1, "d30": 2},
    "documents_top": [],
    "generated_at": "test",
})
assert "لوحة الأسطول تحت السيطرة" in rendered
assert "90%" in rendered
print("modern dashboard template: OK")
