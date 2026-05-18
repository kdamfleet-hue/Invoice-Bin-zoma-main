# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, base64
from data import *

script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, 'output-onlinepngtools.png')
with open(logo_path, 'rb') as f:
    logo_b64 = base64.b64encode(f.read()).decode('utf-8')

html = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>بيان استهلاك الزيوت والفلاتر - فرع الدمام</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;800&display=swap');
:root {{
  --primary: #1a3a5c; --primary-light: #2a5a8c; --accent: #c8a45a;
  --bg: #f8f6f1; --card-bg: #fff; --text: #2c3e50; --text-light: #6b7b8d;
  --border: #e0ddd5; --row-even: #f9f7f2; --row-hover: #eef5ff;
  --shadow: 0 4px 24px rgba(26,58,92,0.08);
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Cairo',sans-serif; background:var(--bg); color:var(--text); line-height:1.7; }}
.page {{ max-width:1100px; margin:0 auto; padding:30px 20px; }}
.header {{ text-align:center; margin-bottom:30px; padding:30px 20px 20px; background:var(--card-bg); border-radius:16px; box-shadow:var(--shadow); border-bottom:3px solid var(--accent); position:relative; overflow:hidden; }}
.header::before {{ content:''; position:absolute; top:0; left:0; right:0; height:4px; background:linear-gradient(135deg,#1a3a5c,#2a5a8c,#1a3a5c); }}
.header img {{ max-width:420px; width:80%; height:auto; margin-bottom:18px; }}
.header h1 {{ font-size:1.3rem; font-weight:700; color:var(--primary); }}
.section {{ background:var(--card-bg); border-radius:16px; box-shadow:var(--shadow); overflow:hidden; margin-bottom:30px; }}
.section-head {{ background:linear-gradient(135deg,#1a3a5c,#2a5a8c,#1a3a5c); color:#fff; padding:16px 24px; font-size:1.1rem; font-weight:700; }}
.section-head.gold {{ background:linear-gradient(135deg,#c8a45a,#a8843a); }}
table {{ width:100%; border-collapse:collapse; font-size:0.92rem; }}
thead th {{ background:var(--primary); color:#fff; padding:14px 12px; font-weight:700; text-align:center; white-space:nowrap; border-left:1px solid rgba(255,255,255,0.15); font-size:0.88rem; }}
thead th:last-child {{ border-left:none; }}
tbody td {{ padding:11px 12px; text-align:center; border-bottom:1px solid var(--border); border-left:1px solid var(--border); transition:background 0.2s; font-size:0.88rem; }}
tbody td:last-child {{ border-left:none; }}
tbody tr:nth-child(even) {{ background:var(--row-even); }}
tbody tr:hover {{ background:var(--row-hover); }}
tbody tr td:first-child {{ font-weight:700; color:var(--primary); width:40px; }}
.plate {{ font-weight:700; direction:rtl; }}
.badge {{ display:inline-block; padding:2px 10px; border-radius:20px; font-size:0.8rem; font-weight:600; }}
.badge-zero {{ background:#f0f0f0; color:#999; }}
.badge-filter {{ background:#eef7ee; color:#27ae60; border:1px solid #c8e6c8; }}
.notes-body {{ padding:24px; }}
.notes-body h3 {{ color:var(--primary); font-size:1.05rem; margin-bottom:8px; padding-bottom:8px; border-bottom:2px solid var(--accent); display:inline-block; }}
.info-box {{ background:#f0f4f8; border-right:4px solid var(--primary); padding:14px 18px; border-radius:0 10px 10px 0; margin:14px 0 20px; font-size:0.95rem; line-height:2; }}
.filter-table {{ width:100%; border-collapse:collapse; margin-top:14px; }}
.filter-table th {{ background:var(--primary); color:#fff; padding:10px; font-size:0.85rem; font-weight:700; text-align:center; }}
.filter-table td {{ padding:8px 12px; border:1px solid var(--border); font-size:0.85rem; }}
.filter-table tr:nth-child(even) {{ background:var(--row-even); }}
.filter-table tr:hover {{ background:var(--row-hover); }}
.filter-table .num {{ text-align:center; font-weight:700; color:var(--primary); width:35px; }}
.filter-table .count {{ text-align:center; font-weight:700; color:var(--primary); width:50px; font-size:0.95rem; }}
.filter-table .name {{ text-align:right; }}
.diesel {{ margin-top:20px; padding-top:18px; border-top:2px dashed var(--border); }}
.diesel-item {{ padding:6px 14px; font-size:0.88rem; }}
.diesel-item.sub {{ color:var(--text-light); font-size:0.82rem; padding-right:34px; }}
.sig {{ display:flex; justify-content:space-between; padding:24px; border-top:2px solid var(--border); margin-top:10px; }}
.sig-block {{ text-align:center; }}
.sig-block .label {{ font-weight:700; color:var(--primary); }}
.sig-block .name {{ color:var(--text-light); font-size:0.88rem; margin-top:4px; }}
.sig-line {{ width:120px; height:2px; background:var(--border); margin:30px auto 0; }}
.closing {{ text-align:center; padding:18px; background:#f0f4f8; border-radius:10px; margin:20px 24px 24px; font-weight:600; color:var(--primary); }}
.footer {{ text-align:center; padding:18px; color:var(--text-light); font-size:0.8rem; }}
@media print {{ body {{ background:#fff; }} .page {{ max-width:100%; padding:10px; }} .section {{ box-shadow:none; border-radius:0; }} tbody tr:hover {{ background:inherit; }} }}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <img src="data:image/png;base64,{logo_b64}" alt="شركة بن زومة">
    <h1>{TITLE}</h1>
  </div>
  <div class="section">
    <div class="section-head">📋 جدول بيان الاستهلاك</div>
    <div style="overflow-x:auto">
      <table>
        <thead><tr>'''

for h in HEADERS:
    html += f'<th>{h}</th>'

html += '</tr></thead><tbody>'

for row in TABLE_DATA:
    html += '<tr>'
    for idx, cell in enumerate(row):
        if idx == 1:
            html += f'<td class="plate">{plate_display(cell)}</td>'
        elif idx == 6:
            if str(cell).strip() == "0":
                html += '<td><span class="badge badge-zero">لا يوجد</span></td>'
            else:
                html += f'<td><span class="badge badge-filter">{cell}</span></td>'
        else:
            html += f'<td>{cell}</td>'
    html += '</tr>'

html += '''</tbody></table></div></div>
  <div class="section">
    <div class="section-head gold">🔧 ملاحظات وتفاصيل الفلاتر</div>
    <div class="notes-body">
      <h3>''' + NOTES_TITLE + '''</h3>
      <div class="info-box">''' + NOTES_SUBTITLE.replace('\n','<br>') + '''</div>
      <h3>''' + FILTERS_TITLE + '''</h3>
      <table class="filter-table">
        <thead><tr><th>م</th><th>نوع الفلتر</th><th>المستهلك</th><th>العدد</th></tr></thead>
        <tbody>'''

for i, (name, orig, count, used) in enumerate(FILTERS_LIST):
    display = f"{name} - {used}" if used else name
    html += f'<tr><td class="num">{i+1}</td><td class="name">{display}</td><td class="count" style="color:#2c3e50">{orig}</td><td class="count">= {count}</td></tr>'

html += '''</tbody></table>
      <div class="diesel"><h3>فلاتر الديزل</h3><div style="margin-top:10px">'''

for d in DIESEL_FILTERS:
    cls = 'diesel-item sub' if d.startswith("تركب") else 'diesel-item'
    prefix = '↳ ' if d.startswith("تركب") else '• '
    html += f'<div class="{cls}">{prefix}{d}</div>'

html += '''</div></div>
      <div class="closing">''' + CLOSING_NOTE.replace('\n','<br>') + '''</div>
      <div class="sig">
        <div class="sig-block"><div class="label">قسم الحركة</div><div class="name">خالد الغامدي</div><div class="sig-line"></div></div>
        <div class="sig-block"><div class="label">التعميد</div><div class="sig-line"></div></div>
      </div>
    </div>
  </div>
  <div class="footer">شركة بن زومة للتجارة الدولية والإنماء المحدودة &copy; 2026</div>
</div>
</body></html>'''

html_path = os.path.join(script_dir, 'بيان_استهلاك_الزيوت_محسن.html')
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"HTML saved: {html_path}")
print("Done!")


