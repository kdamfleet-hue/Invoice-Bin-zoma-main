import re

with open(r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\new_logo_b64.txt', 'r', encoding='utf-8') as f:
    b64 = f.read().strip()

static_path = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\جدول تحسين - Copy\InvoiceApp\index.html'
with open(static_path, 'r', encoding='utf-8') as f:
    s_content = f.read()

# Add logo to the website UI
logo_html = f'<div style="text-align: center; margin-bottom: 2rem;"><img src="data:image/png;base64,{b64}" alt="Logo" style="max-width: 300px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));"></div>\n    <h1 class="header-title">نظام الفواتير الذكي</h1>'

if 'alt="Logo"' not in s_content:
    s_content = s_content.replace('<h1 class="header-title">نظام الفواتير الذكي</h1>', logo_html)
    with open(static_path, 'w', encoding='utf-8') as f:
        f.write(s_content)
    print("Injected logo into static website UI.")



