import re

with open("templates/base.html", "r", encoding="utf-8") as f:
    content = f.read()

new_nav = """<li class="nav-item">
            <a href="/incidents" class="nav-link {% if request.path == '/incidents' %}active{% endif %}">
                <i class="fas fa-exclamation-triangle"></i>
                <span class="nav-text">الحوادث والطوارئ</span>
            </a>
        </li>"""

if "/incidents" not in content:
    content = content.replace('<li class="nav-item">', new_nav + '\n        <li class="nav-item">', 1)
    with open("templates/base.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Added incidents to sidebar.")
else:
    print("Already in sidebar.")
