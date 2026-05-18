import os
import glob
import re

badge_html = '''        {% if google_user %}
        <div class="user-badge" style="position:fixed;top:1.5rem;left:1.5rem;display:flex;align-items:center;gap:8px;background:rgba(255,255,255,0.9);padding:5px 15px;border-radius:50px;box-shadow:0 4px 6px rgba(0,0,0,0.1);z-index:100;backdrop-filter:blur(5px);">
            <img src="{{ google_user.picture }}" alt="Profile" style="width:28px;height:28px;border-radius:50%">
            <span style="font-weight:bold;color:#1A3A5C;font-size:0.9rem">{{ google_user.name }}</span>
            <a href="/logout" style="color:#e74c3c;text-decoration:none;font-size:0.85rem;font-weight:bold;margin-right:8px;transition:var(--trans);">تسجيل خروج</a>
        </div>
        {% endif %}'''

files = glob.glob('templates/*.html')
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Use regex to find and replace the existing google_user block
    pattern = re.compile(r'{%\s*if google_user\s*%}.*?{%\s*endif\s*%}', re.DOTALL)
    
    if pattern.search(content):
        content = pattern.sub(badge_html, content)
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
            print(f'Updated {f}')


