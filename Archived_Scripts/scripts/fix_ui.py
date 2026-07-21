import re

# 1. Fix app_ux.js
app_ux_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\app_ux.js'
with open(app_ux_path, 'r', encoding='utf-8') as f:
    app_ux = f.read()

# First, undo the bad injection at line 2656
app_ux = app_ux.replace("""    // Floating contact dock (WhatsApp + Send-this-table + Email composer), bottom-left, on EVERY tab.
// [REMOVED due to UI conflicts with main dashboard cards and buttons]
function buildFloatingContactDock() {
    // Disabled
}
    if (!tr) return;""", "    if (!tr) return;")

# Second, remove the actual buildFloatingContactDock function
pattern_dock = re.compile(r'// Floating contact dock.*?function buildFloatingContactDock\(\) \{.*?document\.body\.appendChild\(dock\);\s*\}', re.DOTALL)
app_ux = pattern_dock.sub('// Floating dock removed to prevent UI conflicts\nfunction buildFloatingContactDock() {}', app_ux)

with open(app_ux_path, 'w', encoding='utf-8') as f:
    f.write(app_ux)

# 2. Fix schedule.html
sched_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\schedule.html'
with open(sched_path, 'r', encoding='utf-8') as f:
    sched = f.read()

# Replace Tajawal with Cairo for tabs
sched = sched.replace("font-family:'Tajawal',sans-serif;", "font-family:'Cairo',sans-serif; /* Fixed font */")

# Improve button spacing in sched-toolbar
sched = sched.replace(".sched-premium .sched-toolbar { display:flex; flex-wrap:wrap; gap:.6rem; align-items:center; margin:0 0 18px; }",
                      ".sched-premium .sched-toolbar { display:flex; flex-wrap:wrap; gap:12px; align-items:center; justify-content: flex-start; margin:0 0 24px; padding: 12px; background: rgba(0,0,0,0.1); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }")

with open(sched_path, 'w', encoding='utf-8') as f:
    f.write(sched)

print("UI fixes applied to app_ux.js and schedule.html.")
