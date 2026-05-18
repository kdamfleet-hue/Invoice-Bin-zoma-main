# -*- coding: utf-8 -*-
"""Final cleanup: merge known duplicates + fix reversed plates + fix car names."""
import sqlite3, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = os.path.dirname(os.path.abspath(__file__))
db = sqlite3.connect(os.path.join(BASE, 'database.sqlite'))
db.row_factory = sqlite3.Row

# Known duplicate pairs: (keep_name/iqama, delete_name)
# Same person listed twice with slightly different names
DUPLICATES = [
    # كابيل مياه (has iqama) = كاتيل مياة مياة (no iqama, same plate 8714)
    ('كابيل مياه', 'كاتيل مياة مياة'),
    # شومون مياه ادريس مياه (has iqama) = شمون مياه ادريس مياه (no iqama)
    ('شومون مياه ادريس مياه', 'شمون مياه ادريس مياه'),
    # رفيق اسان بيلات (has iqama) = رفيق بيلات بيلات (no iqama)
    ('رفيق اسان بيلات', 'رفيق بيلات بيلات'),
    # محمد عبدالرحمن المندوه (has iqama) = محمد عبدالرحمن السيد المندوه (no iqama)
    ('محمد عبدالرحمن المندوه', 'محمد عبدالرحمن السيد المندوه'),
    # احمد دنقل (has iqama 2441375439) = مارييل فينو داناندان (no iqama, same iqama in old data)
    # Actually these might be different people sharing iqama. Keep both.
]

print("=== Step 1: Merge known duplicates ===")
for keep_name, delete_name in DUPLICATES:
    keep = db.execute("SELECT * FROM drivers WHERE name = ?", (keep_name,)).fetchone()
    delete = db.execute("SELECT * FROM drivers WHERE name = ?", (delete_name,)).fetchone()
    if keep and delete:
        # Merge data from delete into keep
        for field in ['plate', 'car', 'phone', 'empid', 'iqama']:
            kv = keep[field] or ''
            dv = delete[field] or ''
            if dv and not kv:
                db.execute(f"UPDATE drivers SET {field} = ? WHERE id = ?", (dv, keep['id']))
        db.execute("DELETE FROM drivers WHERE id = ?", (delete['id'],))
        print(f"  MERGED: '{delete_name}' -> '{keep_name}'")
    else:
        if not keep: print(f"  NOT FOUND: {keep_name}")
        if not delete: print(f"  NOT FOUND: {delete_name}")

# Fix reversed plates from PDF extraction
print("\n=== Step 2: Fix reversed plates ===")
PLATE_FIXES = {
    'سيف الإسلام': 'أ س م 8033',
    'شوكت علي': 'أ س ق 7821',  
    'شومون مياه ادريس مياه': 'أ س م 8013',
    'كابيل مياه': 'أ س ح 8714',
    'محمد مصلح': 'أ ص ق 6855',
    'موزيد خان': 'أ ر و 4084',
    'احمد دنقل': 'أ س ق 7920',
    'محمد عبدالرحمن المندوه': 'أ س ق 7774',
    'رفيق اسان بيلات': 'أ س ق 7776',
    'اجيت راجا': 'أ ر ل 5580',
}

for name, correct_plate in PLATE_FIXES.items():
    d = db.execute("SELECT * FROM drivers WHERE name = ?", (name,)).fetchone()
    if d:
        old = d['plate'] or '-'
        if old != correct_plate:
            db.execute("UPDATE drivers SET plate = ? WHERE id = ?", (correct_plate, d['id']))
            print(f"  {name}: '{old}' -> '{correct_plate}'")

# Fix reversed car names from PDF
print("\n=== Step 3: Fix reversed car names ===")
CAR_FIXES = {
    'احمد دنقل': '2016 متسوبيشي لوري',
    'محمد عبدالرحمن المندوه': '2016 متسوبيشي لوري',
    'اجيت راجا': '2015 ايسوزو دينا',
}
for name, correct_car in CAR_FIXES.items():
    d = db.execute("SELECT * FROM drivers WHERE name = ?", (name,)).fetchone()
    if d:
        old = d['car'] or '-'
        if 'يرول' in old or 'وزوسيا' in old or 'يشيبوستم' in old or 'انيد' in old or old != correct_car:
            db.execute("UPDATE drivers SET car = ? WHERE id = ?", (correct_car, d['id']))
            print(f"  {name}: '{old}' -> '{correct_car}'")

db.commit()

# Final full list
print(f"\n{'='*80}")
total = db.execute("SELECT COUNT(*) FROM drivers").fetchone()[0]
no_plate = db.execute("SELECT COUNT(*) FROM drivers WHERE plate IS NULL OR plate = '' OR plate = 'None'").fetchone()[0]
no_car = db.execute("SELECT COUNT(*) FROM drivers WHERE car IS NULL OR car = '' OR car = 'None'").fetchone()[0]
no_iqama = db.execute("SELECT COUNT(*) FROM drivers WHERE iqama IS NULL OR iqama = ''").fetchone()[0]
no_phone = db.execute("SELECT COUNT(*) FROM drivers WHERE phone IS NULL OR phone = '' OR phone = 'None'").fetchone()[0]

print(f"  FINAL: {total} drivers | plate=0? {no_plate==0} | car=0? {no_car==0}")
print(f"  Missing: iqama={no_iqama}, phone={no_phone}")
print(f"{'='*80}\n")

drivers = db.execute("SELECT * FROM drivers ORDER BY name").fetchall()
for i, d in enumerate(drivers, 1):
    ok = '✅' if d['plate'] and d['car'] and d['iqama'] and d['phone'] else ('🔶' if d['plate'] and d['car'] else '❌')
    print(f"  {ok} [{i:2d}] {d['name']:<35s} | 🪪 {(d['iqama'] or '-'):<12s} | 🚗 {(d['plate'] or '-'):<12s} | 🚛 {(d['car'] or '-'):<30s} | 📱 {d['phone'] or '-'}")

db.close()



