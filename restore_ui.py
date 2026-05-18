import glob, re, json

# 1. Fix UI: Dark mode removal, Logo fix, Navbar addition
for f in glob.glob('templates/*.html') + ['static/base_styles.css']:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove dark mode button
    content = re.sub(r'<button[^>]*id="darkModeToggle"[^>]*>.*?</button>', '', content, flags=re.DOTALL)
    
    # Remove dark mode css
    content = re.sub(r'body\.dark-mode[^{]*\{[^}]*\}', '', content)
    
    # Fix logo CSS (prevent stretching)
    if '.site-logo {' in content:
        content = re.sub(r'\.site-logo\s*\{[^}]*\}', '.site-logo { width: 450px; max-width: 90%; height: auto; object-fit: contain; margin: 0 auto 1rem auto; display: block; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1)); }', content)
        
    # Add Navbar to top right (if it's index.html or we want it everywhere)
    if '<div class="header-container">' in content and 'bz.sa' not in content:
        nav_html = '''
    <div style="position: absolute; top: 1.5rem; right: 1.5rem; z-index: 100; display: flex; gap: 15px; background: rgba(255,255,255,0.9); padding: 8px 20px; border-radius: 50px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); font-weight: bold; font-size: 0.95rem; border: 1px solid #e1e8ed;">
        <a href="/" style="color: #1A3A5C; text-decoration: none; transition: 0.3s;">الرئيسية</a> |
        <a href="#" style="color: #1A3A5C; text-decoration: none; transition: 0.3s;">من نحن</a> |
        <a href="https://bz.sa" target="_blank" style="color: #1A3A5C; text-decoration: none; transition: 0.3s;">موقعنا الرسمي (bz.sa)</a> |
        <a href="#" style="color: #1A3A5C; text-decoration: none; transition: 0.3s;">تواصل معنا</a>
    </div>
'''
        content = content.replace('<div class="header-container">', nav_html + '\n    <div class="header-container">')

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

# 2. Fix washing schedule print button in schedule.html
with open('templates/schedule.html', 'r', encoding='utf-8') as file:
    content = file.read()
content = content.replace('onclick="window.print()"', 'onclick="generateScheduleExcel()"')
with open('templates/schedule.html', 'w', encoding='utf-8') as file:
    file.write(content)

print("Restored UI fixes and Navbar!")

