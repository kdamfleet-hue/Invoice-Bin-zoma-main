import os
from bs4 import BeautifulSoup

TEMPLATE_DIR = 'templates'
BACKUP_DIR = 'templates_backup'

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def process_template(filepath):
    filename = os.path.basename(filepath)
    if filename in ['base.html', 'login.html', 'index.html', 'absher_import.html']:
        return # Skip base, login, and already processed index.html

    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    if '{% extends' in html:
        return

    # Backup
    with open(os.path.join(BACKUP_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(html)

    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Extract Head content
    head_content = []
    if soup.head:
        for tag in soup.head.find_all(recursive=False):
            if tag.name in ['title', 'meta']:
                continue
            if tag.name == 'link':
                href = tag.get('href', '')
                if 'manifest.json' in href or 'base_styles.css' in href or 'theme.css' in href or 'logo_192' in href or 'fonts.' in href:
                    continue
            if tag.name == 'script':
                src = tag.get('src', '')
                if 'app_ux.js' in src or 'lucide' in src:
                    continue
            head_content.append(str(tag))

    head_str = "\n".join(head_content)

    # 2. Extract Body content
    body_content = ""
    if soup.body:
        # Get inner HTML of body
        body_content = "".join(str(c) for c in soup.body.contents)
    else:
        # Fallback if no body tag
        body_content = html

    # Clean up inline styles that might be setting background again if needed (skip for now)

    # 3. Rebuild with Jinja tags
    new_html = "{% extends 'base.html' %}\n\n"
    
    # Title extraction
    title = "شركة بن زومة"
    if soup.title:
        title = soup.title.string

    new_html += f"{{% block title %}}{title}{{% endblock %}}\n\n"

    if head_str.strip():
        new_html += "{% block head %}\n"
        new_html += head_str
        new_html += "\n{% endblock %}\n\n"

    new_html += "{% block content %}\n"
    new_html += body_content.strip()
    new_html += "\n{% endblock %}\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"Processed {filename}")

for root, _, files in os.walk(TEMPLATE_DIR):
    for file in files:
        if file.endswith('.html'):
            process_template(os.path.join(root, file))

print("✅ Mass refactor completed.")
