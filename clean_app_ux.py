import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\app_ux.js'
with open(file_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Remove the whole <aside> sidebar creation block
# From: // ---- sidebar (cloned from the horizontal nav) ----
# To: document.body.appendChild(aside);
js = re.sub(
    r'// ---- sidebar \(cloned from the horizontal nav\) ----.*?document\.body\.appendChild\(aside\);',
    '// (Sidebar cloning removed, using native topbar as sidebar)',
    js,
    flags=re.DOTALL
)

# Remove the #bzBurger creation
# From: if (brand && !document.getElementById('bzBurger')) {
# To: brand.parentNode.insertBefore(burger, brand);
#         }
js = re.sub(
    r'if \(brand && !document\.getElementById\(\'bzBurger\'\)\) \{.*?brand\.parentNode\.insertBefore\(burger, brand\);\s*\}',
    '// (Old bzBurger removed in favor of native bz-hamburger)',
    js,
    flags=re.DOTALL
)

# Also remove the defensive return
js = js.replace("if (document.querySelector('.bz-sidebar')) return; // already built (defensive)", "// defensive check removed")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("Cleaned up duplicated sidebar logic in app_ux.js!")
