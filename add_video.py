import re

video_html = '''
    <video autoplay muted loop id="myVideo" style="position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%; z-index: -1; object-fit: cover; opacity: 0.3;">
        <source src="{{ url_for('static', filename='login_bg.mp4') }}" type="video/mp4">
    </video>
'''

for f_path in ['templates/login.html', 'templates/password.html']:
    with open(f_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'login_bg.mp4' not in content:
        content = content.replace('<body>', '<body>\n' + video_html)
        # remove body background
        content = content.replace('body {', 'body { background: transparent !important; ')
        
    with open(f_path, 'w', encoding='utf-8') as file:
        file.write(content)
print('Added video to auth pages')
