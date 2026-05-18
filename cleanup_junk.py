# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
db = sqlite3.connect('database.sqlite')
db.execute("DELETE FROM drivers WHERE name = 'تانيدلا ددع'")
db.execute("DELETE FROM drivers WHERE name = 'دونيف لييرام'")
db.commit()
total = db.execute("SELECT COUNT(*) as c FROM drivers").fetchone()[0]
no_plate = db.execute("SELECT COUNT(*) as c FROM drivers WHERE plate IS NULL OR plate = '' OR plate = 'None'").fetchone()[0]
print(f'Total: {total} | Missing plate: {no_plate}')
db.close()
