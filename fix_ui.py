import glob, re

for f in glob.glob('templates/*.html') + ['static/base_styles.css']:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove dark mode button
    content = re.sub(r'<button[^>]*id="darkModeToggle"[^>]*>.*?</button>', '', content, flags=re.DOTALL)
    
    # Remove dark mode css
    content = re.sub(r'body\.dark-mode[^{]*\{[^}]*\}', '', content)
    
    # Fix logo CSS
    if '.site-logo {' in content:
        content = re.sub(r'\.site-logo\s*\{[^}]*\}', '.site-logo { width: 400px; max-width: 90%; height: auto; object-fit: contain; margin: 0 auto 1rem auto; display: block; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1)); }', content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print('Done fixing logo and removing dark mode.')


