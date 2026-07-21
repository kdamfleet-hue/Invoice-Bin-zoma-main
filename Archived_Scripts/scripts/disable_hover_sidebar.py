import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\app_ux.js'
with open(file_path, 'r', encoding='utf-8') as f:
    js = f.read()

# We need to find the call to buildEnterpriseShell() and disable it, 
# or just clear the function body.

# Find the function definition and replace it with an empty function
js = re.sub(
    r'function buildEnterpriseShell\(\)\s*\{[\s\S]*?\}\s*// \-\-\-\- enrich the topbar \-\-\-\-[\s\S]*?catch \(\w+\) \{[^}]*\}[\s\S]*?\}\s*\n',
    'function buildEnterpriseShell() { /* Disabled by user request to keep horizontal topbar */ }\n\n',
    js
)

# Wait, the regex might fail if it doesn't match perfectly. Let's just find where it is called and comment it out.
# Typically it's called inside a DOMContentLoaded event.
js = js.replace('buildEnterpriseShell();', '// buildEnterpriseShell(); /* Disabled */')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(js)

print("buildEnterpriseShell disabled in app_ux.js")
