import os
import re

TEMPLATE_DIR = 'templates'
BACKUP_DIR = 'templates_backup'

# Create backup dir
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def process_template(filepath):
    filename = os.path.basename(filepath)
    if filename in ['base.html', 'login.html']:
        return # Skip base and login
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Backup
    with open(os.path.join(BACKUP_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(content)

    if '{% extends' in content:
        return # Already processed

    # Extract style block if exists
    style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    styles = style_match.group(0) if style_match else ""
    
    # Remove everything from <!DOCTYPE to </head>
    content = re.sub(r'<!DOCTYPE html>.*?</head>', '', content, flags=re.DOTALL)
    
    # Remove <body> and </body> </html>
    content = re.sub(r'<body[^>]*>', '', content)
    content = content.replace('</body>', '').replace('</html>', '')
    
    # Build new content
    new_content = "{% extends 'base.html' %}\n"
    if styles:
        new_content += "{% block head %}\n" + styles + "\n{% endblock %}\n"
        content = content.replace(styles, '')

    new_content += "\n{% block content %}\n"
    new_content += content.strip()
    new_content += "\n{% endblock %}\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

for root, _, files in os.walk(TEMPLATE_DIR):
    for file in files:
        if file.endswith('.html'):
            process_template(os.path.join(root, file))

print("✅ Mass refactor completed.")
