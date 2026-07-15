import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("=== app.py audit ===")
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# Check for duplicate route definitions
routes = re.findall(r'@app\.route\(["\']([^"\']+)', app_content)
from collections import Counter
route_dupes = [(k,v) for k,v in Counter(routes).items() if v > 1]
print(f"Duplicate routes: {route_dupes}")
print(f"Total routes: {len(routes)}")

# Check for unused imports
imports = re.findall(r'^(?:import|from)\s+(\S+)', app_content, re.MULTILINE)
print(f"Total import lines: {len(imports)}")

# Check for `import pandas` inside functions (inefficient)
pd_inside = len(re.findall(r'def \w+.*?import pandas', app_content, re.DOTALL))
print(f"'import pandas' inside functions: {app_content.count('import pandas')}")

# Check app.run at the end
if 'app.run' in app_content:
    print("app.run found: Yes")
else:
    print("app.run found: No (using Gunicorn/Procfile)")

# Check for temporary/scratch files in project
import os
temp_files = []
for f in os.listdir('.'):
    if f.endswith('.bak') or f.startswith('modify_') or f.startswith('merge_'):
        temp_files.append(f)
print(f"Temp/scratch files to clean: {temp_files}")

# Check .gitignore
with open('.gitignore', 'r', encoding='utf-8') as f:
    gitignore = f.read()
print(f".gitignore includes *.xlsx: {'*.xlsx' in gitignore}")
print(f".gitignore includes *.bak: {'*.bak' in gitignore}")
