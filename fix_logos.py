import os
import glob
import re

templates_dir = r"c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-ff9883e6d28109e9447c858bb238652605d2d2df\templates"

for path in glob.glob(os.path.join(templates_dir, "*.html")):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix the typo { url_for -> {{ url_for
    # and also } -> }}
    # Specifically for the top-bar-logo which looks like:
    # <img src="{ url_for('static', filename='site_logo.png') }" alt="شركة بن زومة" class="top-bar-logo">
    content = re.sub(
        r'<img src="\{ url_for\(\'static\', filename=\'site_logo\.png\'\) \}" alt="شركة بن زومة" class="top-bar-logo">',
        r'<img src="{{ url_for(\'static\', filename=\'nav_logo.png\') }}" alt="شركة بن زومة" class="top-bar-logo">',
        content
    )
    
    # If it was already correct:
    content = re.sub(
        r'<img src="\{\{ url_for\(\'static\', filename=\'site_logo\.png\'\) \}\}" alt="شركة بن زومة" class="top-bar-logo">',
        r'<img src="{{ url_for(\'static\', filename=\'nav_logo.png\') }}" alt="شركة بن زومة" class="top-bar-logo">',
        content
    )
    
    # For the big logo (.site-logo or .logo img)
    # It might be: <img src="{{ url_for('static', filename='site_logo.png') }}" ... class="site-logo" ...>
    # Or in index.html: <img src="{{ url_for('static', filename='site_logo.png') }}" alt="Bin Zomah Intl Logo" ...>
    content = content.replace("filename='site_logo.png'", "filename='main_logo.png'")
    
    # Wait, the above replace will also replace any remaining site_logo.png with main_logo.png
    # But we already replaced the top-bar ones with nav_logo.png in the step before! So it's safe.

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
print("Updated all templates with nav_logo.png and main_logo.png and fixed typos.")
