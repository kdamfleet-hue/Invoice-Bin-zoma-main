import re

# 1. Update schedule.html with min-width
file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\schedule.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "width: 100% !important;",
    "width: 100% !important;\n        min-width: 1900px !important;"
)

# Enforce min-width on specific colgroups to prevent squishing
content = content.replace(
    "table.sched td {",
    "table.sched td {\n        min-width: 50px;"
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Add Cache buster to base.html
base_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\base.html'
with open(base_path, 'r', encoding='utf-8') as f:
    base = f.read()

import time
timestamp = str(int(time.time()))
base = re.sub(r'href="\{\{ url_for\(\'static\', filename=\'css/base_styles\.css\'\) \}\}(?:\?v=\d+)?"', f'href="{{{{ url_for(\'static\', filename=\'css/base_styles.css\') }}}}?v={timestamp}"', base)
base = re.sub(r'href="\{\{ url_for\(\'static\', filename=\'css/theme\.css\'\) \}\}(?:\?v=\d+)?"', f'href="{{{{ url_for(\'static\', filename=\'css/theme.css\') }}}}?v={timestamp}"', base)
base = re.sub(r'src="\{\{ url_for\(\'static\', filename=\'app_ux\.js\'\) \}\}(?:\?v=\d+)?"', f'src="{{{{ url_for(\'static\', filename=\'app_ux.js\') }}}}?v={timestamp}"', base)

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(base)

print("min-width added to schedule.html and cache-busters added to base.html")
