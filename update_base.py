import re

with open("templates/base.html", "r", encoding="utf-8") as f:
    content = f.read()

new_links = """
            {% if session.get('is_admin') or session.get('role') == 'operations' %}
            <li><a href="/yard" class="bz-menu-item"><span class="icon">🅿️</span><span class="text">إدارة الساحات (Yard)</span></a></li>
            <li><a href="/custody" class="bz-menu-item"><span class="icon">🔑</span><span class="text">سجل العهد</span></a></li>
            {% endif %}
"""

if "/yard" not in content:
    # insert before <li class="menu-header">الصيانة والتشغيل</li>
    content = content.replace('<li class="menu-header">الصيانة والتشغيل</li>', new_links + '\n            <li class="menu-header">الصيانة والتشغيل</li>')
    with open("templates/base.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Added links to base.html")
else:
    print("Links already exist in base.html")
