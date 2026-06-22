import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the whole <header>...</header> block
content = re.sub(r'<header>.*?</header>', '', content, flags=re.DOTALL)

# Insert the logo inside .header-container
logo_html = """
    <div class="logo" style="text-align: center; margin-bottom: 2rem;">
        <img src="{{ url_for('static', filename='site_logo.png') }}" alt="Bin Zomah Intl Logo" style="height: 180px; filter: drop-shadow(0 8px 12px rgba(0,0,0,0.4)) contrast(1.2) saturate(1.3) brightness(1.05);">
    </div>
"""

content = content.replace('<div class="header-container">', f'<div class="header-container">\n{logo_html}')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated index.html to remove absolute header")
