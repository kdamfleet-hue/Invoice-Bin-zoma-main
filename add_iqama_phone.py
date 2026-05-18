import sys, sqlite3, openpyxl, os
sys.stdout.reconfigure(encoding='utf-8')

# Read phone and iqama data from the Excel file
for f in os.listdir('.'):
    if f.endswith('.xlsx') and 'تحديث' in f and '(1)' not in f and 'template' not in f:
        src = f
        break
else:
    for f in os.listdir('.'):
        if f.endswith('.xlsx') and 'تحديث' in f:
            src = f
            break

print(f'Source: {src}')
wb = openpyxl.load_workbook(src)
ws = wb.active

# Build lookup: name -> {iqama, phone}
driver_info = {}
for r in range(9, ws.max_row + 1):
    name = ws.cell(row=r, column=3).value
    iqama = ws.cell(row=r, column=4).value
    phone = ws.cell(row=r, column=17).value
    if name and name != '————':
        driver_info[str(name).strip()] = {
            'iqama': str(iqama) if iqama else '',
            'phone': str(phone) if phone else ''
        }

print(f'Found {len(driver_info)} drivers with info')
for name, info in list(driver_info.items())[:3]:
    print(f'  {name}: iqama={info["iqama"]}, phone={info["phone"]}')

# Add columns to database if needed
conn = sqlite3.connect('database.sqlite')
c = conn.cursor()

# Check if columns exist
c.execute("PRAGMA table_info(drivers)")
cols = [col[1] for col in c.fetchall()]
print(f'\nCurrent columns: {cols}')

if 'iqama' not in cols:
    c.execute("ALTER TABLE drivers ADD COLUMN iqama TEXT DEFAULT ''")
    print('Added iqama column')
if 'phone' not in cols:
    c.execute("ALTER TABLE drivers ADD COLUMN phone TEXT DEFAULT ''")
    print('Added phone column')

# Update existing drivers with iqama and phone
updated = 0
for name, info in driver_info.items():
    c.execute("UPDATE drivers SET iqama=?, phone=? WHERE name=?", 
              (info['iqama'], info['phone'], name))
    if c.rowcount > 0:
        updated += 1

conn.commit()
print(f'Updated {updated} drivers with iqama/phone data')

# Verify
c.execute("SELECT name, iqama, phone FROM drivers WHERE iqama != '' LIMIT 5")
for r in c.fetchall():
    print(f'  {r[0]}: iqama={r[1]}, phone={r[2]}')

