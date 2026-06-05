import glob, os

navbar_html = '''
    <div style="position: absolute; top: 1.5rem; right: 1.5rem; z-index: 100; display: flex; gap: 15px; background: rgba(255,255,255,0.9); padding: 8px 20px; border-radius: 50px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); font-weight: bold; font-size: 0.95rem; border: 1px solid #e1e8ed;">
        <a href="/" style="color: #1A3A5C; text-decoration: none; transition: 0.3s;">الرئيسية</a> |
        <a href="#" style="color: #1A3A5C; text-decoration: none; transition: 0.3s;">من نحن</a> |
        <a href="https://bz.sa" target="_blank" style="color: #1A3A5C; text-decoration: none; transition: 0.3s;">موقعنا الرسمي (bz.sa)</a> |
        <a href="#" style="color: #1A3A5C; text-decoration: none; transition: 0.3s;">تواصل معنا</a>
    </div>
'''

logo_html = '''
        {% if b64_en %}
            <img src="data:image/png;base64,{{ b64_en }}" alt="Logo" class="site-logo" style="width: 300px; max-width: 90%; height: auto; object-fit: contain; margin: 0 auto 1.5rem auto; display: block; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">
        {% endif %}
'''

for f in ['templates/login.html', 'templates/password.html']:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'bz.sa' not in content:
        content = content.replace('<body>', '<body>\n' + navbar_html)
    
    if 'site-logo' not in content:
        content = content.replace('<div class="login-card glass-surface">', '<div class="login-card glass-surface">\n' + logo_html)
        
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
print('Updated login pages')
