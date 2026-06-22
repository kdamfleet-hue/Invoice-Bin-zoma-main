# -*- coding: utf-8 -*-
"""Recreate database from final_drivers_database.json + all previous corrections."""
import sqlite3, sys, io, os, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'c:\Users\Administrator.MADEBYA-NBLPM4O\Downloads\Invoice-Bin-zoma-main'

db = sqlite3.connect(os.path.join(BASE, 'database.sqlite'))
db.execute("""CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    empid TEXT,
    plate TEXT,
    car TEXT,
    iqama TEXT,
    phone TEXT
)""")
db.execute("DELETE FROM drivers")  # Clear

# Load the best data: combine JSON + previous corrections
json_path = os.path.join(BASE, 'New', 'final_drivers_database.json')
with open(json_path, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# Also load corrections we made previously
corrections_file = os.path.join(BASE, 'New', 'all_drivers_merged.json')
corrections = {}
if os.path.exists(corrections_file):
    with open(corrections_file, 'r', encoding='utf-8') as f:
        cdata = json.load(f)
    if isinstance(cdata, dict):
        for name, data in cdata.items():
            iq = data.get('iqama', '')
            if iq:
                corrections[iq] = data
                corrections[iq]['name'] = name

# Known correct plate/car mappings from ربط_الأسماء and قائمة_المركبات
# (from our previous audit work)
CORRECT_DATA = {
    'أشرف كمال كامل هريدي':       {'plate': 'ر و د 1693',  'car': '2025 سوزوكي DZIRE',      'iqama': '2342453558'},
    'ابراهيم يوسف عوض علي':        {'plate': 'ح ي و 5746',  'car': '2016 كيا سيراتيو',       'iqama': '2249251576'},
    'احمد رشاد محمد شوقى عبد المطلب': {'plate': 'ح ع ن 2874', 'car': '2015 تويوتا كورولا',    'iqama': '2533532608'},
    'احمد محمد زكى شعلان':         {'plate': 'ر ل ر 5063',  'car': '2024 سوزوكي ديز اير',    'iqama': '2596889713'},
    'عبد الرحمن جوده محمد محمود':   {'plate': 'د د و 4282',  'car': '2018 هونداي اكسنت',      'iqama': '2482824873'},
    'عبد الرحمن محمد سعيد البندارى': {'plate': 'ر ل ر 5062', 'car': '2024 سوزوكي ديز اير',    'iqama': '2519087791'},
    'كرم جلال الدين عابد عثمان':    {'plate': 'ر د ب 4650',  'car': '2018 تويوتا كامري',      'iqama': '2578319739'},
    'محمد حسن عبد الرحمن السيد':    {'plate': 'س د ي 2475',  'car': '2026 سوزوكي BALENO',     'iqama': '2494382019'},
    'محمد محمود محمد ابو الحسن':    {'plate': 'ر ل ر 5059',  'car': '2024 سوزوكي ديز اير',    'iqama': '2532825581'},
    'سيف الإسلام':                  {'plate': 'أ س م 8033',  'car': '2023 ايسوزو صندوق مغلق', 'iqama': '2485516401'},
    'شوكت علي':                     {'plate': 'أ س ق 7821',  'car': '2016 متسوبيشي صندوق',   'iqama': '2317876015'},
    'شومون مياه ادريس مياه':        {'plate': 'أ س م 8013',  'car': '2023 ايسوزو صندوق مغلق', 'iqama': '2253252916'},
    'كابيل مياه':                   {'plate': 'أ س ح 8714',  'car': '2023 متسوبيشي صندوق',   'iqama': '2121612820'},
    'محمد مصلح':                    {'plate': 'أ ص ق 6855',  'car': '2024 ايسوزو صندوق مغلق', 'iqama': '2536883693'},
    'موزيد خان':                    {'plate': 'أ ر و 4084',  'car': '2023 ايسوزو صندوق مغلق', 'iqama': '2607260698'},
    'احمد دنقل':                    {'plate': 'أ س ق 7920',  'car': '2016 متسوبيشي لوري',    'iqama': '2441375439'},
    'محمد عبدالرحمن المندوه':       {'plate': 'أ س ق 7774',  'car': '2016 متسوبيشي لوري',    'iqama': '2441077944'},
    'رفيق اسان بيلات':             {'plate': 'أ س ق 7776',  'car': '2016 متسوبيشي صندوق',   'iqama': '2407663372'},
    'اجيت راجا':                    {'plate': 'أ ر ل 5580',  'car': '2015 ايسوزو دينا',      'iqama': '2461544377'},
}

# Known duplicates to skip
SKIP_NAMES = [
    'تم إعداد هذا الجدول بواسطة قسم الحركة',
    '💡 الاستخدام',
    'غير محدد',
    'col',
    'مد سيف الإسلام',  # duplicate of سيف الإسلام
    'هاريس أحمد شوكت علي خان',  # duplicate of شوكت علي
    'مارييل فينود',  # duplicate of احمد دنقل (same iqama)
    'محمد عبدالرحمن السيد المندوه',  # duplicate of محمد عبدالرحمن المندوه
    'محمد مصلح حمادي محسن',  # duplicate of محمد مصلح
    'رفيق بيلات بيلات',  # duplicate of رفيق اسان بيلات
    'كاتيل مياة مياة',  # duplicate of كابيل مياه
    'شمون مياه ادريس مياه',  # duplicate of شومون مياه
    'محمد محمود محمد ابو الحسن',  # will be added from CORRECT_DATA with proper plate
]

# Build final list
final_drivers = []
seen_iqamas = set()

# First add CORRECT_DATA drivers
for name, data in CORRECT_DATA.items():
    iq = data.get('iqama', '')
    # Find phone from raw data
    phone = ''
    for d in raw_data:
        if d.get('iqama') == iq or d.get('name') == name:
            phone = d.get('phone', '')
            if phone:
                break
    if iq in corrections:
        phone = phone or corrections[iq].get('phone', '')
    
    final_drivers.append({
        'name': name,
        'iqama': iq,
        'plate': data['plate'],
        'car': data['car'],
        'phone': phone,
    })
    if iq:
        seen_iqamas.add(iq)

# Then add remaining from raw_data
for d in raw_data:
    name = d.get('name', '')
    if not name or len(name) < 3:
        continue
    if any(s in name for s in SKIP_NAMES):
        continue
    
    iq = d.get('iqama', '')
    if iq and iq in seen_iqamas:
        continue
    
    # Check if name already exists
    if any(f['name'] == name for f in final_drivers):
        continue
    
    plate = d.get('plate', '')
    car = d.get('car', '')
    phone = d.get('phone', '')
    
    final_drivers.append({
        'name': name,
        'iqama': iq,
        'plate': plate,
        'car': car,
        'phone': phone,
    })
    if iq:
        seen_iqamas.add(iq)

# Sort by name
final_drivers.sort(key=lambda x: x['name'])

# Insert into DB
for d in final_drivers:
    db.execute("INSERT INTO drivers (name, plate, car, iqama, phone) VALUES (?, ?, ?, ?, ?)",
        (d['name'], d.get('plate') or None, d.get('car') or None, 
         d.get('iqama') or None, d.get('phone') or None))

db.commit()

# Print final result
print(f"\n{'='*110}")
print(f"  قاعدة بيانات السائقين النهائية: {len(final_drivers)} سائق")
print(f"{'='*110}")
print(f"{'#':>3} | {'الاسم':<35} | {'رقم الإقامة':<12} | {'رقم اللوحة':<14} | {'نوع السيارة':<28} | {'الجوال'}")
print(f"{'-'*3}-+-{'-'*35}-+-{'-'*12}-+-{'-'*14}-+-{'-'*28}-+-{'-'*12}")

for i, d in enumerate(final_drivers, 1):
    s = '✅' if d.get('plate') and d.get('car') and d.get('iqama') and d.get('phone') else '🔶'
    print(f"{s}{i:2d} | {d['name']:<35} | {(d.get('iqama') or '-'):<12} | {(d.get('plate') or '-'):<14} | {(d.get('car') or '-'):<28} | {d.get('phone') or '-'}")

complete = sum(1 for d in final_drivers if d.get('plate') and d.get('car') and d.get('iqama') and d.get('phone'))
no_plate = sum(1 for d in final_drivers if not d.get('plate'))
no_car = sum(1 for d in final_drivers if not d.get('car'))
no_iqama = sum(1 for d in final_drivers if not d.get('iqama'))
no_phone = sum(1 for d in final_drivers if not d.get('phone'))

print(f"\n{'='*60}")
print(f"  ✅ مكتمل: {complete}/{len(final_drivers)}")
print(f"  ناقص لوحة: {no_plate} | سيارة: {no_car} | إقامة: {no_iqama} | جوال: {no_phone}")
print(f"{'='*60}")

db.close()

