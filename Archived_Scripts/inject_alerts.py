import os

app_file = 'app.py'
with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports if missing
imports_to_add = []
if 'import html' not in content:
    imports_to_add.append('import html')
if 'import hmac' not in content:
    imports_to_add.append('import hmac')
if 'from datetime import datetime' not in content:
    imports_to_add.append('from datetime import datetime')

if imports_to_add:
    # Insert right after import os
    content = content.replace('import os', 'import os\n' + '\n'.join(imports_to_add))

alerts_code = """
# ── Expiry Alerts Configuration ──────────────────────────────────────────────
ALERT_RECIPIENTS = [e.strip() for e in os.environ.get("ALERT_RECIPIENTS", "").split(",") if e.strip()]
ALERT_CRON_KEY = os.environ.get("ALERT_CRON_KEY", "")

"""

with open('C:/Users/user/AppData/Local/Temp/extracted_alerts.py', 'r', encoding='utf-8') as f:
    alerts_code += f.read()

# Only append if not already present
if 'def send_expiry_alerts' not in content:
    content += '\n' + alerts_code

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Alerts injected successfully.")
