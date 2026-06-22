with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

btn = '<a href="/logout" style="position: absolute; top: 1.5rem; left: 1.5rem; z-index: 9999; background: #e74c3c; color: white; padding: 8px 20px; border-radius: 50px; font-weight: bold; font-size: 0.95rem; text-decoration: none; font-family: Cairo;">تسجيل الخروج</a>'
wrapped_btn = '{% if not google_user %}' + btn + '{% endif %}'
html = html.replace(btn, wrapped_btn)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
