import os
import glob
import re

templates_dir = r"c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-ff9883e6d28109e9447c858bb238652605d2d2df\templates"

for path in glob.glob(os.path.join(templates_dir, "*.html")):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the escaped quotes
    content = content.replace(r"{{ url_for(\'static\', filename=\'nav_logo.png\') }}", "{{ url_for('static', filename='nav_logo.png') }}")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
print("Fixed template syntax.")
