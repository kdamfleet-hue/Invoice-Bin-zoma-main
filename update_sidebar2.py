import re

with open("templates/base.html", "r", encoding="utf-8") as f:
    content = f.read()

nav_item = """<li class="nav-item">
            <a href="{{ url_for('yard_bp.yard_index') }}" class="nav-link {% if request.endpoint == 'yard_bp.yard_index' %}active{% endif %}">
                <i class="fas fa-parking"></i>
                <span class="nav-text">إدارة الساحات</span>
            </a>
        </li>"""

tires_nav = """<li class="nav-item">
            <a href="{{ url_for('inventory_bp.tires_index') }}" class="nav-link {% if request.endpoint == 'inventory_bp.tires_index' %}active{% endif %}">
                <i class="fas fa-compact-disc"></i>
                <span class="nav-text">سجل الإطارات</span>
            </a>
        </li>
        <li class="nav-item">
            <a href="{{ url_for('inventory_bp.batteries_index') }}" class="nav-link {% if request.endpoint == 'inventory_bp.batteries_index' %}active{% endif %}">
                <i class="fas fa-car-battery"></i>
                <span class="nav-text">سجل البطاريات</span>
            </a>
        </li>"""

if "inventory_bp.tires_index" not in content:
    content = content.replace(nav_item, nav_item + "\n        " + tires_nav)
    with open("templates/base.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Added tires and batteries to sidebar.")
else:
    print("Already in sidebar.")
