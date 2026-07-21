import re

index_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\index.html'
with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

chart_html = """
    <!-- Chart Section -->
    <div class="glass-panel" style="max-width: 1200px; margin: 0 auto 3rem auto; padding: 2rem; position: relative; overflow: hidden;">
        <h3 style="margin-top:0; color: var(--gold-primary); font-family: 'Cairo', sans-serif;">إحصائيات الأسطول </h3>
        <div style="height: 350px; width: 100%;">
            <canvas id="fleetChart"></canvas>
        </div>
    </div>
"""

# Insert chart HTML before <div class="hub-grid">
if 'id="fleetChart"' not in content:
    content = content.replace('<div class="hub-grid">', chart_html + '\n    <div class="hub-grid">')

# Add charts.js to base.html so it loads globally if needed, or just in index.html
# Actually, since charts.js looks for 'fleetChart', I'll just put it in base.html
base_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\base.html'
with open(base_path, 'r', encoding='utf-8') as f:
    base = f.read()

if 'charts.js' not in base:
    base = base.replace(
        '<script defer src="{{ url_for(\'static\', filename=\'app_ux.js\')',
        '<script defer src="{{ url_for(\'static\', filename=\'charts.js\') }}"></script>\n    <script defer src="{{ url_for(\'static\', filename=\'app_ux.js\')'
    )
    with open(base_path, 'w', encoding='utf-8') as f:
        f.write(base)

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("index.html and base.html updated with Chart.js integration.")
