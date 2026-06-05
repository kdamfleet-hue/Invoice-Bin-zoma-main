import os

template_path = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\templates\index.html'
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Move Dark Mode to right
target_btn = 'left: 20px; background: rgba(0,0,0,0.05);'
if target_btn in content:
    content = content.replace(target_btn, 'right: 20px; background: rgba(0,0,0,0.05);')

# 2. Shrink user profile
target_profile_container = '<div style="position: absolute; top: 1rem; left: 1rem; display: flex; align-items: center; gap: 10px; background: rgba(255,255,255,0.9); padding: 5px 15px; border-radius: 50px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'
new_profile_container = '<div style="position: absolute; top: 1rem; left: 1rem; display: flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.9); padding: 3px 10px; border-radius: 50px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'
content = content.replace(target_profile_container, new_profile_container)

content = content.replace('width: 30px; height: 30px;', 'width: 22px; height: 22px;')
content = content.replace('<span style="font-weight: bold; color: #1A3A5C; font-size: 0.9rem;">{{ user.name }}</span>', '<span style="font-weight: bold; color: #1A3A5C; font-size: 0.75rem;">{{ user.name }}</span>')
content = content.replace('<a href="/logout" style="color: #e74c3c; text-decoration: none; font-size: 0.9rem; font-weight: bold; margin-right: 10px;">خروج</a>', '<a href="/logout" style="color: #e74c3c; text-decoration: none; font-size: 0.75rem; font-weight: bold; margin-right: 6px;">خروج</a>')

# Add dark mode for user profile inline
if "body.dark-mode" in content:
    dark_css_patch = """body.dark-mode .user-badge { background: rgba(0,0,0,0.7) !important; border: 1px solid #444; }
        body.dark-mode .user-badge span { color: #82aaff !important; }"""
    if "body.dark-mode .user-badge" not in content:
        content = content.replace('body.dark-mode .header-title', dark_css_patch + '\n        body.dark-mode .header-title')

# Replace inline style with class user-badge to fix dark mode
content = content.replace('style="position: absolute; top: 1rem; left: 1rem; display: flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.9); padding: 3px 10px; border-radius: 50px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"', 'class="user-badge" style="position: absolute; top: 1rem; left: 1rem; display: flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.9); padding: 3px 10px; border-radius: 50px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 10;"')

with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("UI Adjusted")

