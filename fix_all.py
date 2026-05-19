import re
import os

# 1. Fix base_styles.css
css_path = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\Invoice-Bin-zoma-main32232\static\base_styles.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Fix background-clip
css = css.replace('-webkit-background-clip: text;', '-webkit-background-clip: text;\n    background-clip: text;')

# Remove dark mode variables completely
css = re.sub(r'body\.dark-mode\s*{[^}]*}', '', css, flags=re.DOTALL)
# Remove any other dark-mode styles
css = re.sub(r'\.dark-mode\s+[^{]+\s*{[^}]*}', '', css, flags=re.DOTALL)
css = re.sub(r'body\.dark-mode\s+[^{]+\s*{[^}]*}', '', css, flags=re.DOTALL)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

# 2. Fix HTML files
for html_file in ['templates/index.html', 'templates/login.html', 'templates/password.html']:
    path = os.path.join(r'c:\Users\Administrator.MADEBYA-NBLPM4O\Desktop\Invoice-Bin-zoma-main32232', html_file)
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Remove darkModeToggle button
    html = re.sub(r'<button[^>]*id="darkModeToggle"[^>]*>.*?</button>', '', html, flags=re.DOTALL)
    
    # In auth pages, add the video background if not exists
    if html_file in ['templates/login.html', 'templates/password.html']:
        if 'login_bg.mp4' not in html:
            video_html = '''
    <video autoplay muted loop id="myVideo" style="position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%; z-index: -1; object-fit: cover; opacity: 0.3;">
        <source src="{{ url_for('static', filename='login_bg.mp4') }}" type="video/mp4">
    </video>'''
            html = html.replace('<body>', '<body>\n' + video_html)
            # Ensure background is transparent
            if '<style>' in html:
                html = html.replace('body {', 'body { background: transparent !important;')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

print("Fixed CSS and HTML files")
