import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\search.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Always enable the "Add" UI on the search page instead of restricting it to WS
content = content.replace('if (WS) injectAddUI();   // workstation only: show the "add data" form', 'injectAddUI(); // Always show Add form')

# 2. Add an "Edit" button to the employee card
# In cardHtml(e):
card_html_search = r"html \+= '</div>';\s+html \+= '</article>';"
card_html_replace = """html += '</div>';

                // Add an Edit Button that redirects to the Employees tab
                html += '<div style="padding: 0 16px 16px; text-align: center;">';
                html += '<button type="button" class="filter-pill" style="width: 100%; border-color: var(--brand-gold); color: var(--brand-gold);" onclick="window.location.href=\\'/employees\\'">✏️ تعديل في سجل الموظفين</button>';
                html += '</div>';

                html += '</article>';"""

content = re.sub(card_html_search, card_html_replace, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Search page updated with Edit/Add options.")
