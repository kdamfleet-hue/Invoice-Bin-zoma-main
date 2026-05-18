# -*- coding: utf-8 -*-
"""Final rebuild: use the BEST source for each field, merge duplicates properly."""
import sqlite3, sys, io, os, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Downloads\Invoice-Bin-zoma-main'

# Load current DB state (already cleaned in previous steps)
db = sqlite3.connect(os.path.join(BASE, 'database.sqlite'))
db.row_factory = sqlite3.Row
drivers = db.execute("SELECT * FROM drivers ORDER BY name").fetchall()

print(f"Current DB: {len(drivers)} drivers")
print(f"\n{'#':>3} {'الاسم':<35} {'الإقامة':<12} {'اللوحة':<14} {'السيارة':<28} {'الجوال':<12}")
print("-" * 110)

for i, d in enumerate(drivers, 1):
    status = '✅' if d['plate'] and d['car'] and d['iqama'] and d['phone'] else '🔶'
    print(f"{status}{i:2d}  {d['name']:<35} {(d['iqama'] or '-'):<12} {(d['plate'] or '-'):<14} {(d['car'] or '-'):<28} {(d['phone'] or '-'):<12}")

# Count stats
total = len(drivers)
complete = sum(1 for d in drivers if d['plate'] and d['car'] and d['iqama'] and d['phone'])
no_plate = sum(1 for d in drivers if not d['plate'] or d['plate'] in ('', 'None'))
no_car = sum(1 for d in drivers if not d['car'] or d['car'] in ('', 'None'))
no_iqama = sum(1 for d in drivers if not d['iqama'] or d['iqama'] in ('', 'None'))
no_phone = sum(1 for d in drivers if not d['phone'] or d['phone'] in ('', 'None'))

print(f"\n{'='*60}")
print(f"  إجمالي السائقين: {total}")
print(f"  ✅ مكتمل البيانات: {complete}")
print(f"  ناقص لوحة: {no_plate}")
print(f"  ناقص سيارة: {no_car}")
print(f"  ناقص إقامة: {no_iqama}")
print(f"  ناقص جوال: {no_phone}")
print(f"{'='*60}")

db.close()



