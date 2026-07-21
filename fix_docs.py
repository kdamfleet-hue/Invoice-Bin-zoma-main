import re

# 1. Update routes/documents.py
with open("routes/documents.py", "r", encoding="utf-8") as f:
    content = f.read()

import_str = """import threading
from helpers import login_required, load_logo, blob_get, blob_set, audit_and_verify, current_branch_id
"""
content = content.replace("from helpers import login_required, load_logo, blob_get, blob_set, audit_and_verify, current_branch_id\n", import_str)

globals_code = """
_ALERTS_CENTER_LOCK = threading.Lock()
"""
content = content.replace("documents_bp = Blueprint('documents', __name__)\n", "documents_bp = Blueprint('documents', __name__)\n" + globals_code)

with open("routes/documents.py", "w", encoding="utf-8") as f:
    f.write(content)

# 2. Remove from app.py
with open("app.py", "r", encoding="utf-8") as f:
    app_content = f.read()

app_content = re.sub(r'# Serializes the alerts-center.*?_ALERTS_CENTER_LOCK = threading\.Lock\(\)', '', app_content, flags=re.DOTALL)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_content)

print("documents.py updated.")
