import re
import os

html_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Clean the messy inline CSS but KEEP structural layout classes
# We will remove the color overrides and use theme.css variables.
css_to_replace = re.search(r'<style>.*?</style>', content, re.DOTALL)
if css_to_replace:
    cleaned_css = """<style>
        .hub-header { text-align: center; margin: 3rem auto 2rem auto; animation: fadeInDown 0.8s ease; }
        .hub-title { font-size: 3rem; font-weight: 800; color: var(--gold-primary); text-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .stats-wrapper { display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-bottom: 3rem; }
        .stat-circle { width: 150px; height: 150px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; transition: all 0.3s ease; }
        .stat-circle:hover { transform: translateY(-5px); border-color: var(--gold-hover); }
        .stat-circle .count-up { font-size: 2.5rem; font-weight: 800; color: var(--gold-light); }
        .stat-circle span { font-size: 0.9rem; color: var(--text-muted); font-weight: 600; margin-top: 5px; }
        .hub-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; max-width: 1200px; margin: 0 auto 5rem auto; }
        .hub-card { text-align: center; text-decoration: none; padding: 2.5rem 2rem; display: flex; flex-direction: column; align-items: center; gap: 1.5rem; transition: all 0.3s ease; }
        .hub-card:hover { transform: translateY(-8px); border-color: var(--gold-primary); }
        .hub-icon { font-size: 3.5rem; }
        .hub-name { font-size: 1.4rem; font-weight: 700; color: var(--text-main); }
        .hub-desc { font-size: 0.95rem; color: var(--text-muted); line-height: 1.5; }
    </style>"""
    content = content.replace(css_to_replace.group(0), cleaned_css)

# 2. Add glass-panel to hub-card and stat-circle
content = content.replace('class="hub-card"', 'class="hub-card bz-card"')
content = content.replace('class="stat-circle"', 'class="stat-circle glass-panel"')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("index.html refactored.")
