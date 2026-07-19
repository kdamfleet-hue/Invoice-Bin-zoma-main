import re

# 1. Fix Sidebar to be always visible
base_css_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\static\base_styles.css'
with open(base_css_path, 'r', encoding='utf-8') as f:
    css_content = f.read()

# Make sidebar permanently visible
css_content = css_content.replace('right: calc(-260px + 12px) !important; /* 12px peek zone */', 'right: 0 !important; /* Permanently open */')
css_content = css_content.replace('padding-right: 12px !important; /* Space for the peek zone */', 'padding-right: 260px !important; /* Space for permanent sidebar */')

# Remove the peek zone line
css_content = re.sub(r'\.bz-topbar::before\s*{[^}]+}', '', css_content, flags=re.DOTALL)
css_content = re.sub(r'\.bz-topbar:hover::before\s*{[^}]+}', '', css_content, flags=re.DOTALL)

with open(base_css_path, 'w', encoding='utf-8') as f:
    f.write(css_content)


# 2. Fix Clickable Stats and Notifications
fleet_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\fleet_dashboard.html'
with open(fleet_path, 'r', encoding='utf-8') as f:
    fleet_content = f.read()

# Add onclicks to stats cards
fleet_content = fleet_content.replace('<div class="fd-stat">', '<div class="fd-stat" onclick="window.location.href=\'/employees\'" style="cursor: pointer;" title="الانتقال إلى الموظفين">')

# But some specific ones can go to schedule
fleet_content = fleet_content.replace('<div class="fd-stat" onclick="window.location.href=\'/employees\'" style="cursor: pointer;" title="الانتقال إلى الموظفين">\n<div class="st-val" id="stActive2"', '<div class="fd-stat" onclick="window.location.href=\'/schedule\'" style="cursor: pointer;" title="الانتقال إلى الجدول الأسبوعي">\n<div class="st-val" id="stActive2"')

# Add onclick to notification items
fleet_content = fleet_content.replace('<li class="fd-noti-item ${isUrgent ? \'urgent\' : \'warn\'}">', '<li class="fd-noti-item ${isUrgent ? \'urgent\' : \'warn\'}" onclick="window.location.href=\'/employees\'" style="cursor: pointer;" title="الانتقال لتحديث الوثيقة">')

with open(fleet_path, 'w', encoding='utf-8') as f:
    f.write(fleet_content)

print("Sidebar permanently opened and clickable links added.")
