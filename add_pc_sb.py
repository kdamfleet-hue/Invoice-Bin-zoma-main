import re

with open("templates/base.html", "r", encoding="utf-8") as f:
    content = f.read()

new_nav = """<li class="nav-item">
            <a href="{{ url_for('finance_bp.petty_cash_index') }}" class="nav-link {% if request.endpoint == 'finance_bp.petty_cash_index' %}active{% endif %}">
                <i class="fas fa-wallet"></i>
                <span class="nav-text">العهد والمصاريف</span>
            </a>
        </li>"""

if "finance_bp.petty_cash_index" not in content:
    content = content.replace('<li class="nav-item">', new_nav + '\n        <li class="nav-item">', 1)
    with open("templates/base.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Added petty cash to sidebar.")
else:
    print("Already in sidebar.")
