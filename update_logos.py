import os
import glob

templates_dir = r"c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-ff9883e6d28109e9447c858bb238652605d2d2df\templates"

for path in glob.glob(os.path.join(templates_dir, "*.html")):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace nav logo in top-bar
    # It might be {{ url_for('static', filename='site_logo.png') }} or { url_for... }
    # We can just replace 'site_logo.png' with 'nav_logo.png' for the class="top-bar-logo"
    
    # Simple replace:
    content = content.replace("filename='site_logo.png') }}\" alt=\"شركة بن زومة\" class=\"top-bar-logo\"", "filename='nav_logo.png') }}\" alt=\"شركة بن زومة\" class=\"top-bar-logo\"")
    
    # Also in index.html, the main logo:
    if "index.html" in path:
        content = content.replace("filename='site_logo.png') }}\" alt=\"Bin Zomah Intl Logo\"", "filename='main_logo.png') }}\" alt=\"Bin Zomah Intl Logo\"")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
print("Updated all logos")
