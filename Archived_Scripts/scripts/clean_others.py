import re

files_to_clean = [
    r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\washing.html',
    r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\employees.html'
]

for file_path in files_to_clean:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Unify buttons
    content = content.replace('class="btn-primary"', 'class="btn-neon success"')
    content = content.replace('class="btn-outline"', 'class="btn-neon"')
    content = content.replace('class="btn-submit-gold"', 'class="btn-neon"')
    content = content.replace('class="btn-submit-orange"', 'class="btn-neon"')
    content = content.replace('class="btn-danger"', 'class="btn-neon danger"')
    content = content.replace('class="action-btn"', 'class="btn-neon"')
    
    # Unify layout
    content = content.replace('class="actions-bar"', 'class="bz-actions-bar"')
    content = content.replace('class="emp-actions"', 'class="bz-actions-bar"')
    
    # Unify cards
    content = content.replace('class="card"', 'class="bz-card"')
    content = content.replace('class="glass-panel"', 'class="bz-card"')
    
    # Unify tables
    content = content.replace('id="washTable"', 'id="washTable" class="bz-table"')
    content = content.replace('id="employeesTable"', 'id="employeesTable" class="bz-table"')

    # Clean conflicting CSS
    css_match = re.search(r'<style>.*?</style>', content, re.DOTALL)
    if css_match:
        old_css = css_match.group(0)
        new_css = re.sub(r'\.btn-.*?\s*{[^}]+}', '', old_css, flags=re.DOTALL)
        new_css = re.sub(r'\.actions-bar\s*{[^}]+}', '', new_css, flags=re.DOTALL)
        content = content.replace(old_css, new_css)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Washing and Employees HTML refactored.")
