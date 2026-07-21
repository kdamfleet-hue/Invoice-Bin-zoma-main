import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

def extract_function(name, content):
    pattern = r'(?:@app\.route\([^)]+\)\s*(?:@login_required\s*)?)+def ' + name + r'\([^)]*\):.*?(?=\n(?:@app\.route|def )\s*|\n\n\n|\Z)'
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        return match.group(0), content.replace(match.group(0), "")
    return "", content
    
funcs = [
    "fleet_dashboard", "employees_page", "api_employees",
    "get_drivers", "add_driver", "delete_driver", "bulk_delete_drivers", "update_driver",
    "update_driver_field", "sync_excel", "api_fleet_data", "sync_all_from_drivers"
]

extracted = []
for name in funcs:
    code, content = extract_function(name, content)
    if code:
        extracted.append(code)

out_py = """import re
import json
import io
import base64
import openpyxl
import logging
from datetime import datetime, date
from flask import Blueprint, render_template, session, request, jsonify
from helpers import login_required, load_logo, blob_get, blob_set, audit_and_verify, current_branch_id
from models.schema import db, Driver

logger = logging.getLogger("InvoiceApp")
fleet_bp = Blueprint('fleet', __name__)

""" + "\n\n".join(extracted).replace("@app.route(", "@fleet_bp.route(")

with open("routes/fleet.py", "w", encoding="utf-8") as f:
    f.write(out_py)
    
# Register blueprint in app.py
content = content.replace("app.register_blueprint(schedule_bp)", "app.register_blueprint(schedule_bp)\nfrom routes.fleet import fleet_bp\napp.register_blueprint(fleet_bp)")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Fleet blueprint extracted.")
