import re

file_path = r'c:\Users\user\OneDrive\Desktop\Invoice-Bin-zoma-main-main\templates\schedule.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the Javascript col sums so they add up exactly to 93 (so 93+2+5 = 100%)
# MAIN_COLS
content = re.sub(
    r"const MAIN_COLS = \[.*?\];",
    """const MAIN_COLS = [
      { key: 'empid',      label: 'الرقم الوظيفي',            w: 4 },
      { key: 'name',       label: 'اسم السائق',               w: 12 },
      { key: 'iqama',      label: 'رقم الإقامة',              w: 5 },
      { key: 'job',        label: 'الوظيفة',                  w: 4 },
      { key: 'plate',      label: 'رقم اللوحة',               w: 5 },
      { key: 'model',      label: 'الموديل',                  w: 4 },
      { key: 'vtype',      label: 'نوع المركبة',              w: 5 },
      { key: 'pallets',    label: 'عدد الطبالي',              w: 3 },
      { key: 'load',       label: 'الحمولة',                  w: 3 },
      { key: 'vserial',    label: 'الرقم التسلسلي',           w: 5 },
      { key: 'inspect',    label: 'تاريخ انتهاء الفحص الدوري', w: 6, date: true },
      { key: 'rem_days1',  label: 'الأيام المتبقية',          w: 3, readonly: true },
      { key: 'license',    label: 'تاريخ انتهاء رخصة السير',   w: 6, date: true },
      { key: 'rem_days2',  label: 'الأيام المتبقية',          w: 3, readonly: true },
      { key: 'drivercard', label: 'تاريخ انتهاء بطاقة السائق', w: 6, date: true },
      { key: 'rem_days3',  label: 'الأيام المتبقية',          w: 3, readonly: true },
      { key: 'opcard',     label: 'تاريخ انتهاء بطاقة التشغيل', w: 6, date: true },
      { key: 'rem_days4',  label: 'الأيام المتبقية',          w: 3, readonly: true },
      { key: 'empNotes',   label: 'الملاحظات',                w: 6 },
      { key: 'phone',      label: 'رقم الجوال',               w: 4 }
    ];""",
    content,
    flags=re.DOTALL
)

# SPARE_COLS
content = re.sub(
    r"const SPARE_COLS = \[.*?\];",
    """const SPARE_COLS = [
      { key: 'status',     label: 'الحالة',                   w: 6 },
      { key: 'plate',      label: 'رقم اللوحة',               w: 6 },
      { key: 'model',      label: 'الموديل',                  w: 5 },
      { key: 'vtype',      label: 'نوع المركبة',              w: 8 },
      { key: 'pallets',    label: 'عدد الطبالي',              w: 5 },
      { key: 'load',       label: 'الحمولة',                  w: 5 },
      { key: 'vserial',    label: 'الرقم التسلسلي',           w: 7 },
      { key: 'inspect',    label: 'تاريخ انتهاء الفحص الدوري', w: 8, date: true },
      { key: 'rem_days1',  label: 'الأيام المتبقية',          w: 5, readonly: true },
      { key: 'license',    label: 'تاريخ انتهاء رخصة السير',   w: 8, date: true },
      { key: 'rem_days2',  label: 'الأيام المتبقية',          w: 5, readonly: true },
      { key: 'opcard',     label: 'تاريخ انتهاء بطاقة التشغيل', w: 8, date: true },
      { key: 'rem_days3',  label: 'الأيام المتبقية',          w: 5, readonly: true },
      { key: 'empNotes',   label: 'الملاحظات',                w: 12 }
    ];""",
    content,
    flags=re.DOTALL
)

# VAC_COLS
content = re.sub(
    r"const VAC_COLS = \[.*?\];",
    """const VAC_COLS = [
      { key: 'empid',      label: 'الرقم الوظيفي',            w: 10 },
      { key: 'name',       label: 'اسم السائق',               w: 20 },
      { key: 'iqama',      label: 'رقم الإقامة',              w: 10 },
      { key: 'job',        label: 'الوظيفة',                  w: 10 },
      { key: 'drivercard', label: 'تاريخ انتهاء بطاقة السائق', w: 10, date: true },
      { key: 'rem_days1',  label: 'الأيام المتبقية',          w: 8, readonly: true },
      { key: 'phone',      label: 'رقم الجوال',               w: 10 },
      { key: 'empNotes',   label: 'الملاحظات',                w: 15 }
    ];""",
    content,
    flags=re.DOTALL
)

# 2. Fix the nbLabel issue which causes horizontal overflow and breaks table alignment
# Replace: const nbLabel = s => escapeHtml(s).split(' ').map(w => `<span class="nb">${w}</span>`).join(' ');
content = content.replace(
    r"const nbLabel = s => escapeHtml(s).split(' ').map(w => `<span class=\"nb\">${w}</span>`).join(' ');",
    r"const nbLabel = s => escapeHtml(s);"
)

# 3. Add explicit fixed-layout CSS to make sure columns strictly respect percentages
css_injection = """
    /* Fixed table alignment */
    table.sched {
        table-layout: fixed !important;
        width: 100% !important;
        word-wrap: break-word !important;
    }
    table.sched th {
        white-space: normal !important;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 0.8rem;
        text-align: center;
        padding: 8px 4px !important;
    }
    table.sched td {
        overflow: hidden;
        padding: 4px !important;
    }
    table.sched input {
        width: 100% !important;
        box-sizing: border-box !important;
    }
"""

content = content.replace('</style>', css_injection + '\n  </style>')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("schedule.html table columns aligned and fixed!")
