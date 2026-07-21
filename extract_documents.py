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
    "documents_page", "api_documents", "delete_legacy_doc", "get_legacy_doc_file",
    "alerts_page", "api_alert_settings", "alerts_center_update",
    "api_expiry_alerts_preview", "send_expiry_alerts", "cron_expiry_alerts"
]

extracted = []
for name in funcs:
    code, content = extract_function(name, content)
    if code:
        extracted.append(code)

out_py = """import re
import json
import base64
import logging
from datetime import datetime
from flask import Blueprint, render_template, session, request, jsonify, send_file
from helpers import login_required, load_logo, blob_get, blob_set, audit_and_verify, current_branch_id
from models.schema import db, Driver, Document

logger = logging.getLogger("InvoiceApp")
documents_bp = Blueprint('documents', __name__)

""" + "\n\n".join(extracted).replace("@app.route(", "@documents_bp.route(")

with open("routes/documents.py", "w", encoding="utf-8") as f:
    f.write(out_py)
    
# Register blueprint in app.py
content = content.replace("app.register_blueprint(fleet_bp)", "app.register_blueprint(fleet_bp)\nfrom routes.documents import documents_bp\napp.register_blueprint(documents_bp)")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Documents blueprint extracted.")
