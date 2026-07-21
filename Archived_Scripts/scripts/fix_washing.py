import re
import os

# 1. Modify washing.html to hide previous months on UI
washing_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\washing.html'
with open(washing_path, 'r', encoding='utf-8') as f:
    washing_html = f.read()

# Modify markCurrentMonthHeader()
old_mark_header = """    function markCurrentMonthHeader() {
        for (let i = 0; i < 12; i++) {
            const th = document.getElementById('mhead-' + i);
            if (th) th.classList.toggle('current-month', i === CURRENT_MONTH);
        }
        const msName = document.getElementById('msMonthName');
        if (msName) msName.textContent = MONTH_NAMES[CURRENT_MONTH];
    }"""
new_mark_header = """    function markCurrentMonthHeader() {
        for (let i = 0; i < 12; i++) {
            const th = document.getElementById('mhead-' + i);
            if (!th) continue;
            if (i === CURRENT_MONTH) {
                th.classList.add('current-month');
                th.style.display = 'table-cell'; // Show only current month
            } else {
                th.classList.remove('current-month');
                th.style.display = 'none'; // Hide all other months from UI
            }
        }
        const msName = document.getElementById('msMonthName');
        if (msName) msName.textContent = MONTH_NAMES[CURRENT_MONTH];
    }"""
if old_mark_header in washing_html:
    washing_html = washing_html.replace(old_mark_header, new_mark_header)

# Modify renderTable td logic
old_td_loop = """            for (let mi = 0; mi < 12; mi++) {
                const w = v.m[mi];
                const cur = mi === CURRENT_MONTH ? ' current-month' : '';
                const mark = w ? '<span class="ok-mark" title="استلم">✓</span>'
                               : '<span class="x-mark" title="لم يستلم">✗</span>';
                html += `<td class="cell-wash ${w ? 'washed' : 'not-washed'}${cur}" onclick="toggle(${idx},${mi})" title="${escapeHtml(MONTH_NAMES[mi])}: ${w ? 'استلم' : 'لم يستلم'}">${mark}</td>`;
            }"""
new_td_loop = """            for (let mi = 0; mi < 12; mi++) {
                const w = v.m[mi];
                const cur = mi === CURRENT_MONTH ? ' current-month' : '';
                const mark = w ? '<span class="ok-mark" title="استلم">✓</span>'
                               : '<span class="x-mark" title="لم يستلم">✗</span>';
                const disp = (mi === CURRENT_MONTH) ? '' : 'style="display:none;"';
                html += `<td class="cell-wash ${w ? 'washed' : 'not-washed'}${cur}" ${disp} onclick="toggle(${idx},${mi})" title="${escapeHtml(MONTH_NAMES[mi])}: ${w ? 'استلم' : 'لم يستلم'}">${mark}</td>`;
            }"""
if old_td_loop in washing_html:
    washing_html = washing_html.replace(old_td_loop, new_td_loop)

with open(washing_path, 'w', encoding='utf-8') as f:
    f.write(washing_html)


# 2. Add Employee Sync logic to app.py
app_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\app.py'
with open(app_path, 'r', encoding='utf-8') as f:
    app_code = f.read()

sync_func = """
def _sync_from_employees_to_fleet():
    try:
        from modules.db_utils import db_connection, blob_get, blob_set
        with db_connection() as db:
            c = db.cursor()
            c.execute("SELECT name, plate, job FROM hr_employees")
            emp_rows = c.fetchall()
        
        # Build map of plate -> name
        emp_map = {}
        for r in emp_rows:
            name = str(r[0] or '').strip()
            plate = str(r[1] or '').strip()
            if name and plate:
                np = plate.replace(' ', '').lower()
                emp_map[np] = {'name': name, 'plate': plate, 'type': str(r[2] or '').strip()}
        
        if not emp_map:
            return
            
        # Update Schedule
        sched = blob_get("schedule_data")
        if isinstance(sched, list):
            changed = False
            for v in sched:
                np = str(v.get("plate", "")).replace(' ', '').lower()
                if np in emp_map and v.get("driver") != emp_map[np]['name']:
                    v["driver"] = emp_map[np]['name']
                    changed = True
            if changed:
                blob_set("schedule_data", sched)
                
        # Update Washing
        washing = blob_get("washing_schedule")
        if isinstance(washing, list):
            w_changed = False
            for v in washing:
                np = str(v.get("plate", "")).replace(' ', '').lower()
                if np in emp_map and v.get("driver") != emp_map[np]['name']:
                    v["driver"] = emp_map[np]['name']
                    w_changed = True
            if w_changed:
                blob_set("washing_schedule", washing)
                
    except Exception as e:
        import logging
        logging.exception(f"sync_from_employees error: {e}")
"""

if "_sync_from_employees_to_fleet" not in app_code:
    app_code += sync_func

# Inject call into employees_data
if "blob_set(\"employees\", rows)" in app_code and "_sync_from_employees_to_fleet()" not in app_code:
    app_code = app_code.replace('blob_set("employees", rows)', 'blob_set("employees", rows)\n            _sync_from_employees_to_fleet()')

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_code)

print("Washing UI fixed and Employee sync logic injected.")
