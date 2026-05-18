import sqlite3
import pandas as pd
import os

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'database.sqlite'
excel_path = 'قائمة_السائقين_والمركبات_المدمجة_النهائية.xlsx'

conn = sqlite3.connect(db_path)

# استخراج البيانات مع ترتيبها وتسمية الأعمدة بالعربية
query = """
SELECT 
    id AS 'التسلسل',
    name AS 'اسم السائق',
    iqama AS 'رقم الإقامة',
    empid AS 'الرقم الوظيفي',
    plate AS 'رقم اللوحة',
    car AS 'السيارة/الموديل',
    phone AS 'رقم الجوال'
FROM drivers
ORDER BY name ASC
"""

df = pd.read_sql_query(query, conn)
conn.close()

# دمج الاسم مع رقم الإقامة ورقم اللوحة والجوال والموديل في عمود واحد
df['البيانات المدمجة (اسم - إقامة - لوحة - جوال - موديل)'] = (
    df['اسم السائق'].fillna('لا يوجد').astype(str) + ' - ' + 
    df['رقم الإقامة'].replace('', 'بدون إقامة').fillna('بدون إقامة').astype(str) + ' - ' + 
    df['رقم اللوحة'].replace('', 'بدون لوحة').fillna('بدون لوحة').astype(str) + ' - ' +
    df['رقم الجوال'].replace('', 'بدون جوال').fillna('بدون جوال').astype(str) + ' - ' +
    df['السيارة/الموديل'].replace('', 'بدون موديل').fillna('بدون موديل').astype(str)
)

# حفظ البيانات في ملف إكسيل
df.to_excel(excel_path, index=False, engine='openpyxl')
print(f"تم تصدير البيانات بنجاح إلى ملف {excel_path}")



