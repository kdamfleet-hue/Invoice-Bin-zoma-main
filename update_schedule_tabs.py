import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\schedule.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace <button class="sp-tab active" with <button class="bz-tab active"
html = html.replace('class="sp-tab active"', 'class="bz-tab active"')
html = html.replace('class="sp-tab"', 'class="bz-tab"')

# The bz-tabs container currently has a default margin-bottom: 24px in theme.css
# Let's adjust schedule.html so that the tables align perfectly
html = html.replace('<div class="bz-tabs">', '<div class="bz-tabs" style="margin: 0 auto 20px auto; max-width: 1900px; justify-content: center;">')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("schedule.html tabs updated!")
