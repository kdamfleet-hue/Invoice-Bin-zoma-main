import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\schedule.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# I will replace standard classes to match theme.css
# 1. Update sched-toolbar to bz-actions-bar
content = content.replace('class="sched-toolbar"', 'class="bz-actions-bar"')

# 2. Update all specific buttons
content = content.replace('class="btn-primary"', 'class="btn-neon success"')
content = content.replace('class="btn-outline"', 'class="btn-neon"')
content = content.replace('class="btn-submit-gold"', 'class="btn-neon"')
content = content.replace('class="btn-danger"', 'class="btn-neon danger"')
content = content.replace('class="sched-btn"', 'class="btn-neon"')
content = content.replace('class="action-btn"', 'class="btn-neon"')
content = content.replace('class="sp-tab"', 'class="bz-tab"')
content = content.replace('class="sp-tabs"', 'class="bz-tabs"')

# 3. Tables
content = content.replace('<table class="bz-fit" id="tableMain">', '<table class="bz-table" id="tableMain">')
content = content.replace('<table class="bz-fit" id="tableSpare">', '<table class="bz-table" id="tableSpare">')
content = content.replace('<table class="bz-fit" id="tableVacation">', '<table class="bz-table" id="tableVacation">')

# 4. Clean up inline styles that conflict
css_match = re.search(r'<style>.*?</style>', content, re.DOTALL)
if css_match:
    old_css = css_match.group(0)
    # We will just strip out anything that conflicts or keep it minimal
    # Since schedule.html has 200 lines of very specific table layouts (col widths), I will keep it but remove the buttons and colors that I've unified.
    new_css = re.sub(r'\.btn-.*?\s*{[^}]+}', '', old_css, flags=re.DOTALL) # remove old btn styles
    new_css = re.sub(r'\.sched-toolbar\s*{[^}]+}', '', new_css, flags=re.DOTALL)
    new_css = re.sub(r'\.sp-tabs?\s*{[^}]+}', '', new_css, flags=re.DOTALL)
    content = content.replace(old_css, new_css)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("schedule.html refactored.")
