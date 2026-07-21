import re

with open("templates/users_admin.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the <select id="role"> options
old_select = """<select id="role" required>
                    <option value="" disabled selected>-- اختر الصلاحية --</option>
                    <option value="admin">مدير عام (Admin)</option>
                    <option value="branch_manager">مدير فرع (Branch Manager)</option>
                    <option value="data_entry">مدخل بيانات (Data Entry)</option>
                    <option value="viewer">مُطلع (Viewer)</option>
                    <option value="kiosk">محطة عمل / خدمة ذاتية (Kiosk)</option>
                </select>"""
                
new_select = """<select id="role" required>
                    <option value="" disabled selected>-- اختر الصلاحية --</option>
                    <option value="admin">مدير أسطول / مسؤول (Admin)</option>
                    <option value="operations">قسم الحركة (Operations)</option>
                    <option value="maintenance">قسم الصيانة (Maintenance)</option>
                    <option value="finance">قسم الحسابات (Finance)</option>
                    <option value="viewer">مُطلع (Viewer)</option>
                    <option value="kiosk">محطة عمل / ورشة (Kiosk)</option>
                </select>"""

if old_select in content:
    content = content.replace(old_select, new_select)
else:
    # use regex
    pattern = r'<select id="role" required>.*?</select>'
    content = re.sub(pattern, new_select, content, flags=re.DOTALL)

# Replace the roleMap
old_map = """const roleMap = {
                'admin': 'مدير عام',
                'branch_manager': 'مدير فرع',
                'data_entry': 'مدخل بيانات',
                'viewer': 'مُطلع',
                'kiosk': 'محطة عمل'
            };"""
            
new_map = """const roleMap = {
                'admin': 'مدير الأسطول',
                'operations': 'قسم الحركة',
                'maintenance': 'قسم الصيانة',
                'finance': 'قسم الحسابات',
                'viewer': 'مُطلع',
                'kiosk': 'محطة عمل / ورشة'
            };"""

if old_map in content:
    content = content.replace(old_map, new_map)
else:
    pattern_map = r'const roleMap = \{.*?^\s*\};'
    content = re.sub(pattern_map, new_map, content, flags=re.MULTILINE|re.DOTALL)

with open("templates/users_admin.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated users_admin.html roles.")
