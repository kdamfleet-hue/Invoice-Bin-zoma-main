import os
import re

mapping = {
    'index': 'dashboard.index',
    'dashboard': 'dashboard.dashboard',
    'kpis': 'dashboard.kpis',
    'handover': 'dashboard.handover',
    
    'oils': 'operations.oils',
    'fuel': 'operations.fuel',
    'purchase': 'operations.purchase',
    'workshop': 'operations.workshop',
    'records': 'operations.records',
    'incidents': 'operations.incidents',
    
    'schedule': 'schedule.schedule',
    'washing': 'schedule.washing',
    
    'system_features': 'system.system_features',
    'snapshots': 'system.snapshots',
    
    'tracking': 'gps.tracking',
    'gps_dashboard': 'gps.gps_dashboard',
    'gps_devices': 'gps.gps_devices',
    'gps_sync': 'gps.gps_sync',
    
    'fleet_dashboard': 'fleet.fleet_dashboard',
    'employees': 'fleet.employees_page',
    
    'documents': 'documents.documents_page',
    'alerts': 'documents.alerts_page',
}

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original = content
    for old, new in mapping.items():
        # url_for("old") or url_for('old') or url_for("old", ...)
        content = re.sub(r'url_for\([\'"]' + old + r'[\'"]', f'url_for("{new}"', content)
        # also handle url_for without kwargs but with spaces just in case
        
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

dirs = ['routes', 'templates']
changed = 0
for d in dirs:
    if not os.path.exists(d): continue
    for root, _, files in os.walk(d):
        for file in files:
            if file.endswith('.py') or file.endswith('.html'):
                if process_file(os.path.join(root, file)):
                    changed += 1

# Also check app.py
if process_file('app.py'):
    changed += 1

print(f"Updated url_for in {changed} files.")
