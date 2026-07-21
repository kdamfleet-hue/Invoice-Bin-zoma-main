import re
import os

base_css_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\base_styles.css'
with open(base_css_path, 'r', encoding='utf-8') as f:
    css_content = f.read()

# I added a section called "/* Transform Topbar into Hover Sidebar */" all the way to the end of the file.
# I will use regex to find and remove it.
# Actually, I'll just find the start of my additions and truncate the file there.
# Let's search for "/* Transform Topbar into Hover Sidebar */"

start_idx = css_content.find("/* Transform Topbar into Hover Sidebar */")
if start_idx != -1:
    css_content = css_content[:start_idx]
    with open(base_css_path, 'w', encoding='utf-8') as f:
        f.write(css_content.strip())
    print("Sidebar CSS completely removed. Reverted to Topbar.")
else:
    # If not found, let's try to remove .bz-topbar { position: fixed !important; right: 0 ...
    print("Could not find the exact comment, looking for .bz-topbar fixed styles.")
    # We will do a regex to remove all bz-topbar rules at the end of the file that have !important
    # Wait, earlier I ran fix_sidebar.py which appended things. Let's look at what fix_sidebar.py did.
    pass

# We also need to restore the duplicate header in fleet_dashboard.html?
# NO! The user hated the "duplicate header appearing distortedly over the page". They just want the topbar from base.html to sit normally at the top of the page.
