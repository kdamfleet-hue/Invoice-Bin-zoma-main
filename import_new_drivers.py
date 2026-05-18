import pandas as pd
import sqlite3
import sys
import io
import math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

excel_path = r"c:\Users\Administrator.MADEBYA-NBLPM4O\Downloads\vehicle_list_excel_without_qr-code_2026-05-18.xlsx"
db_path = "database.sqlite"

# Read excel starting from row 12 (index 11)
df = pd.read_excel(excel_path, header=11)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

added = 0
updated = 0

for idx, row in df.iterrows():
    plate = str(row.get('رقم اللوحة', '')).strip()
    brand = str(row.get('الماركة', '')).strip()
    model = str(row.get('الطراز', '')).strip()
    year = str(row.get('سنة الصنع', '')).strip()
    
    iqama = str(row.get('رقم هوية المستخدم الفعلي', '')).strip()
    name = str(row.get('اسم المستخدم الفعلي', '')).strip()
    
    if plate == 'nan' or not plate:
        continue
        
    if iqama == '-' or iqama == 'nan':
        iqama = None
    if name == '-' or name == 'nan' or name == '' or name is None:
        name = "لا يوجد"
        
    car = f"{year} {brand} {model}".replace('nan', '').strip()
    
    # Check if driver exists by iqama or plate
    driver = None
    if iqama:
        c.execute("SELECT * FROM drivers WHERE iqama = ?", (iqama,))
        driver = c.fetchone()
        
    if not driver and plate:
        c.execute("SELECT * FROM drivers WHERE plate = ?", (plate,))
        driver = c.fetchone()
        
    if driver:
        # Update
        updates = []
        vals = []
        if plate and driver['plate'] != plate:
            updates.append("plate = ?")
            vals.append(plate)
        if car and driver['car'] != car:
            updates.append("car = ?")
            vals.append(car)
        if iqama and driver['iqama'] != iqama:
            updates.append("iqama = ?")
            vals.append(iqama)
        if name and driver['name'] != name:
            updates.append("name = ?")
            vals.append(name)
            
        if updates:
            vals.append(driver['id'])
            query = "UPDATE drivers SET " + ", ".join(updates) + " WHERE id = ?"
            c.execute(query, vals)
            updated += 1
    else:
        # Insert
        c.execute("INSERT INTO drivers (name, plate, car, iqama) VALUES (?, ?, ?, ?)", (name, plate, car, iqama))
        added += 1

conn.commit()
total = c.execute("SELECT count(*) FROM drivers").fetchone()[0]
conn.close()

print(f"تم الانتهاء بنجاح!")
print(f"المركبات المضافة الجديدة: {added}")
print(f"المركبات التي تم تحديث بياناتها: {updated}")
print(f"إجمالي العدد في قاعدة البيانات: {total}")
