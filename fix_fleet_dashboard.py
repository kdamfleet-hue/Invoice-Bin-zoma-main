import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\fleet_dashboard.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the duplicate <header class="bz-topbar">...</header>
header_match = re.search(r'<header class="bz-topbar">.*?</header>', content, re.DOTALL)
if header_match:
    content = content.replace(header_match.group(0), '')

# 2. Change fd-shell to bz-shell to align with the rest of the application
content = content.replace('class="fd-shell"', 'class="bz-shell"')

# 3. Change fd-card to bz-card for unified styling
content = content.replace('class="fd-card"', 'class="bz-card"')

# 4. Remove all messy inline styles that conflict with theme.css
css_match = re.search(r'<style>.*?</style>', content, re.DOTALL)
if css_match:
    old_css = css_match.group(0)
    # We strip out color and layout definitions that bz-card / theme.css already handles
    new_css = re.sub(r'\.fd-card\s*{[^}]+}', '', old_css, flags=re.DOTALL)
    new_css = re.sub(r'\.fd-shell\s*{[^}]+}', '', new_css, flags=re.DOTALL)
    new_css = re.sub(r'\.fd-topbar\s*{[^}]+}', '', new_css, flags=re.DOTALL)
    new_css = re.sub(r'\.bz-topbar\s*{[^}]+}', '', new_css, flags=re.DOTALL)
    content = content.replace(old_css, new_css)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("fleet_dashboard.html fixed.")
