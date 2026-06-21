import os
import re

navbar_template = """    <!-- Top Navigation Bar -->
    <div class="top-bar">
        <img src="{{ url_for('static', filename='site_logo.png') }}" alt="شركة بن زومة" class="top-bar-logo">
        <div class="top-bar-title">
            {ICON} {TITLE}
            <span>فرع الدمام — شركة بن زومة للتجارة والإنماء</span>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <div class="top-nav-links">
                <a href="/">🏠 الرئيسية</a>
                <a href="/purchase">🛒 شراء</a>
                <a href="/schedule">📋 جدول</a>
                <a href="/oils">🛢 زيوت</a>
                <a href="/employees">👥 موظفين</a>
                <a href="/washing">🚿 غسيل</a>
                <a href="/workshop">🔧 صيانة</a>
            </div>
            <button id="darkModeToggle" onclick="toggleDarkMode()" style="border:none;font-size:1.1rem;cursor:pointer;border-radius:50%;width:34px;height:34px;display:flex;align-items:center;justify-content:center;box-shadow:var(--shadow-sm);background:var(--surface-hover);">🌙</button>
            <a href="/logout" style="background:#e74c3c;color:white;padding:5px 14px;border-radius:20px;font-weight:bold;font-size:0.8rem;text-decoration:none;">خروج</a>
        </div>
    </div>"""

pages = {
    'index.html': ('🏠', 'الرئيسية (نظام الفواتير)'),
    'oils.html': ('🛢', 'بيان زيوت وفلاتر'),
    'purchase.html': ('🛒', 'طلب شراء وإصلاح'),
    'schedule.html': ('📋', 'الجدول الأسبوعي'),
    'washing.html': ('🚿', 'جدول الغسيل'),
    'employees.html': ('👥', 'بيانات الموظفين'),
    'gps_sync.html': ('🛰', 'مزامنة كشف GPS'),
    'tracking.html': ('🛰', 'التتبع المباشر'),
    'workshop.html': ('🔧', 'تقرير صيانة الورشة')
}

templates_dir = r"c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-ff9883e6d28109e9447c858bb238652605d2d2df\templates"

for filename, (icon, title) in pages.items():
    path = os.path.join(templates_dir, filename)
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove existing .top-bar completely
    content = re.sub(r'<!-- Top Navigation Bar -->\s*<div class="top-bar">.*?</div>\s*</div>', '', content, flags=re.DOTALL)
    
    nav_html = navbar_template.format(ICON=icon, TITLE=title)
    
    # Inject right after video if exists, else body
    if '</video>' in content:
        content = content.replace('</video>', f'</video>\n\n{nav_html}')
    else:
        content = content.replace('<body>', f'<body>\n\n{nav_html}')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {filename}")
