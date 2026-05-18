# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
db = sqlite3.connect('database.sqlite')
db.row_factory = sqlite3.Row

total = db.execute('SELECT COUNT(*) as c FROM drivers').fetchone()['c']
no_plate = db.execute("SELECT COUNT(*) as c FROM drivers WHERE plate IS NULL OR plate = '' OR plate = 'None'").fetchone()['c']
no_car = db.execute("SELECT COUNT(*) as c FROM drivers WHERE car IS NULL OR car = '' OR car = 'None'").fetchone()['c']
no_iqama = db.execute("SELECT COUNT(*) as c FROM drivers WHERE iqama IS NULL OR iqama = '' OR iqama = 'None'").fetchone()['c']

print(f'Total drivers: {total}')
print(f'Missing plate: {no_plate}')
print(f'Missing car:   {no_car}')
print(f'Missing iqama: {no_iqama}')
print()
print('== Drivers missing plate OR car: ==')
rows = db.execute("""SELECT name, iqama, plate, car, phone FROM drivers 
    WHERE (plate IS NULL OR plate = '' OR plate = 'None') 
    OR (car IS NULL OR car = '' OR car = 'None') 
    ORDER BY name""").fetchall()
for r in rows:
    name = r['name']
    iq = r['iqama'] or '-'
    pl = r['plate'] or '-'
    ca = r['car'] or '-'
    ph = r['phone'] or '-'
    print(f'  {name} | iqama={iq} | plate={pl} | car={ca} | phone={ph}')
db.close()

