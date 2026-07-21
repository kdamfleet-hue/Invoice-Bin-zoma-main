import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\fleet_dashboard.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace ANY instance of fd-card with bz-card
content = re.sub(r'\bfd-card\b', 'bz-card', content)
content = re.sub(r'\bglass-panel\b', 'bz-card', content) # Ensure we don't have bz-card bz-card
content = content.replace('bz-card bz-card', 'bz-card')

# Replace tables
content = content.replace('class="fd-table"', 'class="bz-table"')
content = content.replace('id="fleetTable"', 'id="fleetTable" class="bz-table"')

# Inputs
content = content.replace('id="fdSearch"', 'id="fdSearch" class="bz-input"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("fleet_dashboard.html fully polished.")
