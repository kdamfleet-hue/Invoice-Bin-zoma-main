import os
import re
import base64

def update_logo():
    # Read the new logo base64
    with open('logo_excel.png', 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')
    
    # Update templates/index.html
    html_path = 'templates/index.html'
    if os.path.exists(html_path):
        content = open(html_path, 'r', encoding='utf-8').read()
        content = re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+', 'data:image/png;base64,'+b64, content)
        open(html_path, 'w', encoding='utf-8').write(content)
        print("Updated templates/index.html")

    # Update index.html
    html_path2 = 'index.html'
    if os.path.exists(html_path2):
        content2 = open(html_path2, 'r', encoding='utf-8').read()
        content2 = re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+', 'data:image/png;base64,'+b64, content2)
        open(html_path2, 'w', encoding='utf-8').write(content2)
        print("Updated index.html")

update_logo()
