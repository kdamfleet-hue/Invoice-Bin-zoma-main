from pathlib import Path
from jinja2 import Environment, FileSystemLoader

root = Path(__file__).resolve().parents[1]
env = Environment(loader=FileSystemLoader(root / "templates"))
env.parse((root / "templates" / "drivers_info.html").read_text(encoding="utf-8"))
text = (root / "templates" / "drivers_info.html").read_text(encoding="utf-8")
for needle in ["queueDriverSuggest", "queueVehicleSuggest", "selectDriverSuggestion", "selectVehicleSuggestion", "edit_reason"]:
    assert needle in text, needle
print("autocomplete template syntax/content: OK")
