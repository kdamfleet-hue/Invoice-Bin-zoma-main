# -*- coding: utf-8 -*-
"""Fix duplicates: merge drivers with same iqama, keep the one with most data, delete duplicates."""
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db = sqlite3.connect('database.sqlite')
db.row_factory = sqlite3.Row

# Get all drivers
all_drivers = db.execute("SELECT * FROM drivers ORDER BY name").fetchall()
print(f"Total drivers before fix: {len(all_drivers)}")

# Group by iqama
iqama_groups = {}
for d in all_drivers:
    iq = (d['iqama'] or '').strip()
    if iq and len(iq) >= 8:
        if iq not in iqama_groups:
            iqama_groups[iq] = []
        iqama_groups[iq].append(dict(d))

# Find duplicates and merge
merged_count = 0
deleted_ids = []

for iq, group in iqama_groups.items():
    if len(group) <= 1:
        continue
    
    # Find the best record (most data + longest name)
    def score(d):
        s = 0
        if d.get('plate') and d['plate'] != 'None': s += 10
        if d.get('car') and d['car'] != 'None': s += 10
        if d.get('phone') and d['phone'] != 'None': s += 5
        if d.get('empid') and d['empid'] != 'None': s += 3
        s += len(d.get('name', ''))  # prefer longer names
        return s
    
    group.sort(key=score, reverse=True)
    best = group[0]
    
    # Merge all data into best
    for other in group[1:]:
        for field in ['plate', 'car', 'phone', 'empid', 'iqama']:
            other_val = other.get(field, '')
            best_val = best.get(field, '')
            if other_val and other_val != 'None' and (not best_val or best_val == 'None'):
                best[field] = other_val
    
    # Update the best record
    db.execute("""UPDATE drivers SET name=?, empid=?, plate=?, car=?, iqama=?, phone=? WHERE id=?""",
        (best['name'], best.get('empid') or None, best.get('plate') or None, 
         best.get('car') or None, best.get('iqama') or None, best.get('phone') or None, best['id']))
    
    # Delete duplicates
    for other in group[1:]:
        db.execute("DELETE FROM drivers WHERE id=?", (other['id'],))
        deleted_ids.append(other['id'])
        print(f"  MERGED: '{other['name']}' (id={other['id']}) -> '{best['name']}' (id={best['id']})")
    
    merged_count += 1

db.commit()

# Show results
remaining = db.execute("SELECT COUNT(*) as c FROM drivers").fetchone()['c']
no_plate = db.execute("SELECT COUNT(*) as c FROM drivers WHERE plate IS NULL OR plate = '' OR plate = 'None'").fetchone()['c']
no_car = db.execute("SELECT COUNT(*) as c FROM drivers WHERE car IS NULL OR car = '' OR car = 'None'").fetchone()['c']

print(f"\n{'='*60}")
print(f"Merged groups: {merged_count}")
print(f"Deleted duplicates: {len(deleted_ids)}")
print(f"Remaining drivers: {remaining}")
print(f"Still missing plate: {no_plate}")
print(f"Still missing car:   {no_car}")

# Show remaining gaps
print(f"\n== Still missing plate/car after merge: ==")
rows = db.execute("""SELECT name, iqama, plate, car, phone FROM drivers 
    WHERE (plate IS NULL OR plate = '' OR plate = 'None') 
    OR (car IS NULL OR car = '' OR car = 'None') 
    ORDER BY name""").fetchall()
for r in rows:
    print(f"  {r['name']} | iqama={r['iqama'] or '-'} | plate={r['plate'] or '-'} | car={r['car'] or '-'}")

db.close()
