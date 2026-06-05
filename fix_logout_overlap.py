import glob

print("Fixing overlapping logout buttons in all templates")

injected_btn = '<a href="/logout" style="position: absolute; top: 1.5rem; left: 1.5rem; z-index: 9999; background: #e74c3c; color: white; padding: 8px 20px; border-radius: 50px; font-weight: bold; font-size: 0.95rem; text-decoration: none; font-family: Cairo; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">تسجيل الخروج</a>'
wrapped_btn = '{% if not google_user %}' + injected_btn + '{% endif %}'

for file in glob.glob('templates/*.html'):
    with open(file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    if injected_btn in html:
        html = html.replace(injected_btn, wrapped_btn)
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Fixed {file}")

print("Done.")
