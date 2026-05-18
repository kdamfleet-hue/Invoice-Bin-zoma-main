# -*- coding: utf-8 -*-
"""Extract driver-vehicle data from the main PDF table and update SQLite database."""
import pdfplumber, sqlite3, sys, io, os, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.path.dirname(os.path.abspath(__file__))

pdf_path = os.path.join(BASE, "نسخة من تحديث المركبات والسائقين-الدمام2026 -5-3 تم اضافه ارقام الاقامه-1 (3).p.pdf")

# Column mapping (RTL table - columns are reversed)
# R2: ['0546635123', ...data..., 'انيد وزوسيا', '2023', '4141 و ر ا', 'عزوم', '2327676793', 'دمحا يعافر يبنلادبع ءلاع', '100162', '1']
# Index: 0=phone, 9=car_type, 10=model, 11=plate, 12=job, 13=iqama, 14=name, 15=empid, 16=m

COL_PHONE = 0
COL_CAR = 9
COL_MODEL = 10
COL_PLATE = 11
COL_JOB = 12
COL_IQAMA = 13
COL_NAME = 14
COL_EMPID = 15

def reverse_arabic(text):
    """Sometimes PDF extracts Arabic text reversed."""
    if not text:
        return ''
    return text.strip()

pdf = pdfplumber.open(pdf_path)
all_rows = []

for page in pdf.pages:
    tables = page.extract_tables()
    for table in tables:
        for row in table:
            if not row or len(row) < 15:
                continue
            clean = [str(c).strip() if c else '' for c in row]
            
            name = clean[COL_NAME] if COL_NAME < len(clean) else ''
            iqama = clean[COL_IQAMA] if COL_IQAMA < len(clean) else ''
            plate = clean[COL_PLATE] if COL_PLATE < len(clean) else ''
            car = clean[COL_CAR] if COL_CAR < len(clean) else ''
            model = clean[COL_MODEL] if COL_MODEL < len(clean) else ''
            phone = clean[COL_PHONE] if COL_PHONE < len(clean) else ''
            empid = clean[COL_EMPID] if COL_EMPID < len(clean) else ''
            
            # Skip headers and empty rows
            if not iqama or len(iqama) < 8 or 'ةماقلإا' in iqama or '————' in iqama:
                continue
            
            # Combine car type + model
            full_car = f"{model} {car}".strip() if model and car else car or model
            
            entry = {
                'name': name,
                'iqama': iqama,
                'plate': plate,
                'car': full_car,
                'phone': phone,
                'empid': empid,
            }
            all_rows.append(entry)
            print(f"  Found: {name} | iqama={iqama} | plate={plate} | car={full_car} | phone={phone}")

pdf.close()
print(f"\nTotal entries from PDF: {len(all_rows)}")

# Now update the database
db = sqlite3.connect(os.path.join(BASE, 'database.sqlite'))
db.row_factory = sqlite3.Row

updated = 0
added = 0

for entry in all_rows:
    iqama = entry['iqama']
    
    # Find by iqama
    driver = db.execute("SELECT * FROM drivers WHERE iqama = ?", (iqama,)).fetchone()
    
    if driver:
        # Update missing fields
        changes = {}
        if entry['plate'] and (not driver['plate'] or driver['plate'] in ('', 'None')):
            changes['plate'] = entry['plate']
        if entry['car'] and (not driver['car'] or driver['car'] in ('', 'None')):
            changes['car'] = entry['car']
        if entry['phone'] and entry['phone'] != '————' and (not driver['phone'] or driver['phone'] in ('', 'None')):
            changes['phone'] = entry['phone']
        if entry['empid'] and (not driver['empid'] or driver['empid'] in ('', 'None')):
            changes['empid'] = entry['empid']
        
        if changes:
            sets = ', '.join(f"{k} = ?" for k in changes.keys())
            vals = list(changes.values()) + [driver['id']]
            db.execute(f"UPDATE drivers SET {sets} WHERE id = ?", vals)
            updated += 1
            print(f"  UPDATED: {driver['name']} <- {changes}")
    else:
        # Driver not in DB, add if has a name
        if entry['name']:
            db.execute("INSERT INTO drivers (name, empid, plate, car, iqama, phone) VALUES (?, ?, ?, ?, ?, ?)",
                (entry['name'], entry['empid'] or None, entry['plate'] or None, 
                 entry['car'] or None, iqama, entry['phone'] or None))
            added += 1
            print(f"  ADDED: {entry['name']}")

db.commit()

# Final stats
total = db.execute('SELECT COUNT(*) as c FROM drivers').fetchone()['c']
no_plate = db.execute("SELECT COUNT(*) as c FROM drivers WHERE plate IS NULL OR plate = '' OR plate = 'None'").fetchone()['c']
no_car = db.execute("SELECT COUNT(*) as c FROM drivers WHERE car IS NULL OR car = '' OR car = 'None'").fetchone()['c']

print(f"\n{'='*60}")
print(f"Updated: {updated} | Added: {added}")
print(f"Total drivers: {total}")
print(f"Still missing plate: {no_plate}")
print(f"Still missing car: {no_car}")
print(f"{'='*60}")

# Show remaining gaps
if no_plate > 0:
    print("\nDrivers still missing plate:")
    rows = db.execute("SELECT name, iqama FROM drivers WHERE plate IS NULL OR plate = '' OR plate = 'None' ORDER BY name").fetchall()
    for r in rows:
        print(f"  {r['name']} (iqama={r['iqama'] or '-'})")

db.close()
