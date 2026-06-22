import glob, re

navbar_html = '''
    <div class="top-nav-bar" style="position: absolute; top: 1.5rem; right: 1.5rem; z-index: 100; display: flex; gap: 15px; background: rgba(255,255,255,0.9); padding: 8px 20px; border-radius: 50px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); font-weight: bold; font-size: 0.95rem; border: 1px solid #e1e8ed;">
        <a href="/" style="color: #1A3A5C; text-decoration: none; transition: 0.3s;">الرئيسية</a> |
        <a href="#" style="color: #1A3A5C; text-decoration: none; transition: 0.3s;">من نحن</a> |
        <a href="https://bz.sa" target="_blank" style="color: #1A3A5C; text-decoration: none; transition: 0.3s;">موقعنا الرسمي (bz.sa)</a> |
        <a href="#" style="color: #1A3A5C; text-decoration: none; transition: 0.3s;">تواصل معنا</a>
    </div>
'''

for f_path in glob.glob('templates/*.html'):
    with open(f_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove existing bz.sa navbar if exists so we don't duplicate
    if 'bz.sa' in content:
        content = re.sub(r'<div[^>]*>[\s\n]*<a href="/"[^>]*>الرئيسية.*?</div>', '', content, flags=re.DOTALL)
    
    # Insert right after <body>
    content = content.replace('<body>', '<body>\n' + navbar_html)
    
    with open(f_path, 'w', encoding='utf-8') as file:
        file.write(content)
print('Added navbar to all pages')
