import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\schedule.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Make the table head gradient and sleek
content = content.replace(
    'background:rgba(0,0,0,.28);',
    'background:linear-gradient(180deg, rgba(11, 13, 20, 0.9), rgba(19, 23, 34, 0.95));'
)
# Add hover effect to the table rows
content = content.replace(
    '.sched-premium table.sched tbody tr { transition:background .15s; }',
    '.sched-premium table.sched tbody tr { transition:all 0.3s ease; }\n    .sched-premium table.sched tbody tr:hover td:not(.exp-bad):not(.exp-warn) { background: rgba(197, 160, 89, 0.12) !important; transform: scale(1.001); box-shadow: 0 4px 15px rgba(0,0,0,0.2); }'
)

# Update the table wrapper to be a glass panel
content = content.replace(
    'class="sched-table-wrap"',
    'class="sched-table-wrap glass-panel"'
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("schedule.html tables upgraded.")
