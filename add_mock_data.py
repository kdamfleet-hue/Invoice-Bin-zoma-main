import sqlite3
import os

db_path = 'database.sqlite'
conn = sqlite3.connect(db_path)
c = conn.cursor()

mock_data = [
    ('أحمد محمد', 'أ ب ت 1234', 'تويوتا كامري'),
    ('خالد عبدالله', 'س ص ع 5678', 'هيونداي إلنترا'),
    ('سعيد اليامي', 'د ر و 9012', 'فورد تورس'),
    ('عمر الدوسري', 'هـ ط ق 3456', 'ايسوزو دينا'),
    ('فهد المطيري', 'ك ل م 7890', 'نيسان صني')
]

for name, plate, car in mock_data:
    c.execute('INSERT INTO drivers (name, plate, car) VALUES (?, ?, ?)', (name, plate, car))

conn.commit()
conn.close()

print("تمت إضافة 5 أسماء وسيارات تجريبية بنجاح إلى قاعدة البيانات.")
