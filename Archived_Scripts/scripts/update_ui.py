import re

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Add theme.css if not present
    if 'css/theme.css' not in html:
        html = html.replace("</head>", "  <link rel=\"stylesheet\" href=\"{{ url_for('static', filename='css/theme.css', v=30) }}\">\n</head>")

    # Replace specific styles to blend with theme.css
    html = html.replace('var(--fd-bg)', 'var(--bg-dark)')
    html = html.replace('var(--fd-surface)', 'var(--bg-panel)')
    html = html.replace('var(--fd-surface2)', 'rgba(59, 130, 246, 0.1)') # neon tint
    html = html.replace('var(--fd-border)', 'var(--border-glass)')
    html = html.replace('var(--fd-text)', 'var(--text-main)')
    html = html.replace('var(--fd-gold)', 'var(--accent-primary)')
    html = html.replace('var(--fd-gold2)', 'var(--accent-primary)')
    html = html.replace('font-family: \'Tajawal\', sans-serif;', 'font-family: var(--font-arabic);')

    # Update classes to use glass-panel
    html = html.replace('class="fd-card"', 'class="fd-card glass-panel"')
    html = html.replace('class="fd-kpi"', 'class="fd-kpi glass-panel"')
    html = html.replace('class="fd-kpi ', 'class="fd-kpi glass-panel ')

    # Keep the specific background in KPIs but blend it
    html = html.replace('class="ab-btn"', 'class="ab-btn btn-neon"')
    html = html.replace('class="btn btn-primary"', 'class="btn-neon"')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated {filepath}")

update_file('templates/fleet_dashboard.html')
update_file('templates/schedule.html')
