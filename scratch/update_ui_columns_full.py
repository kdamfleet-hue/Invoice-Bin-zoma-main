import re

with open('templates/schedule.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace column definitions
new_cols_script = """
    const MAIN_COLS = [
      { key: 'empid',      label: 'الرقم الوظيفي',            w: 5 },
      { key: 'name',       label: 'اسم السائق',               w: 12 },
      { key: 'iqama',      label: 'رقم الإقامة',              w: 6 },
      { key: 'job',        label: 'الوظيفة',                  w: 5 },
      { key: 'plate',      label: 'رقم اللوحة',               w: 5 },
      { key: 'model',      label: 'الموديل',                  w: 4 },
      { key: 'vtype',      label: 'نوع المركبة',              w: 6 },
      { key: 'pallets',    label: 'عدد الطبالي',              w: 4 },
      { key: 'load',       label: 'الحمولة',                  w: 4 },
      { key: 'vserial',    label: 'الرقم التسلسلي',           w: 5 },
      { key: 'inspect',    label: 'تاريخ انتهاء الفحص الدوري', w: 6, date: true },
      { key: 'rem_days1',  label: 'الأيام المتبقية',          w: 4, readonly: true },
      { key: 'license',    label: 'تاريخ انتهاء رخصة السير',   w: 6, date: true },
      { key: 'rem_days2',  label: 'الأيام المتبقية',          w: 4, readonly: true },
      { key: 'drivercard', label: 'تاريخ انتهاء بطاقة السائق', w: 6, date: true },
      { key: 'rem_days3',  label: 'الأيام المتبقية',          w: 4, readonly: true },
      { key: 'opcard',     label: 'تاريخ انتهاء بطاقة التشغيل', w: 6, date: true },
      { key: 'rem_days4',  label: 'الأيام المتبقية',          w: 4, readonly: true },
      { key: 'empNotes',   label: 'الملاحظات',                w: 6 },
      { key: 'phone',      label: 'رقم الجوال',               w: 5 }
    ];

    const SPARE_COLS = [
      { key: 'status',     label: 'الحالة',                   w: 7 },
      { key: 'plate',      label: 'رقم اللوحة',               w: 6 },
      { key: 'model',      label: 'الموديل',                  w: 5 },
      { key: 'vtype',      label: 'نوع المركبة',              w: 8 },
      { key: 'pallets',    label: 'عدد الطبالي',              w: 5 },
      { key: 'load',       label: 'الحمولة',                  w: 5 },
      { key: 'vserial',    label: 'الرقم التسلسلي',           w: 7 },
      { key: 'inspect',    label: 'تاريخ انتهاء الفحص الدوري', w: 7, date: true },
      { key: 'rem_days1',  label: 'الأيام المتبقية',          w: 5, readonly: true },
      { key: 'license',    label: 'تاريخ انتهاء رخصة السير',   w: 7, date: true },
      { key: 'rem_days2',  label: 'الأيام المتبقية',          w: 5, readonly: true },
      { key: 'opcard',     label: 'تاريخ انتهاء بطاقة التشغيل', w: 7, date: true },
      { key: 'rem_days3',  label: 'الأيام المتبقية',          w: 5, readonly: true },
      { key: 'empNotes',   label: 'الملاحظات',                w: 9 }
    ];

    const VAC_COLS = [
      { key: 'empid',      label: 'الرقم الوظيفي',            w: 8 },
      { key: 'name',       label: 'اسم السائق',               w: 16 },
      { key: 'iqama',      label: 'رقم الإقامة',              w: 10 },
      { key: 'job',        label: 'الوظيفة',                  w: 8 },
      { key: 'drivercard', label: 'تاريخ انتهاء بطاقة السائق', w: 10, date: true },
      { key: 'rem_days1',  label: 'الأيام المتبقية',          w: 8, readonly: true },
      { key: 'phone',      label: 'رقم الجوال',               w: 10 },
      { key: 'empNotes',   label: 'الملاحظات',                w: 12 }
    ];

    function colsFor(section) {
      if (section === 'main') return MAIN_COLS;
      if (section === 'spare') return SPARE_COLS;
      if (section === 'vacation') return VAC_COLS;
      return MAIN_COLS;
    }
"""

html = re.sub(
    r'const MAIN_COLS = \[.*?\].*?function colsFor\(section\) \{.*?\}',
    new_cols_script.strip(),
    html,
    flags=re.DOTALL
)

with open('templates/schedule.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated full columns in schedule.html")
