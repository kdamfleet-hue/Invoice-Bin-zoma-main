import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\fleet_dashboard.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace .bz-card with .glass-panel for all main sections
content = content.replace('class="bz-card"', 'class="glass-panel"')
# Add a margin to them so they don't look cramped
content = content.replace('class="glass-panel"', 'class="glass-panel" style="margin-top:20px; overflow:hidden;"')

# Enhance the bz-card-head to be sleek
content = content.replace(
    'class="bz-card-head"',
    'class="bz-card-head" style="background: rgba(11, 13, 20, 0.4); border-bottom: 1px solid rgba(197, 160, 89, 0.2);"'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("fleet_dashboard.html updated with glass panels.")
