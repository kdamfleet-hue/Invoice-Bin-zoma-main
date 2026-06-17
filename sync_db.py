import sqlite3
import json
import os

db_path = 'database.db'
json_path = 'static/employees_default.json'

def sync_database():
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS drivers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  empid TEXT,
                  name TEXT,
                  iqama TEXT,
                  job TEXT,
                  phone TEXT,
                  plate TEXT,
                  car TEXT)''')

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_count = 0
    inserted_count = 0

    for row in data:
        if len(row) < 10: continue
        empid = str(row[0]).strip()
        iqama = str(row[1]).strip()
        name = str(row[2]).strip()
        job = str(row[6]).strip()
        phone = str(row[7]).strip()
        plate = str(row[9]).strip()
        car = str(row[36]).strip() + ' ' + str(row[38]).strip() if len(row) > 38 else ''
        car = car.strip()
        
        if not name or name == 'nan' or name == 'None':
            continue
            
        c.execute('SELECT id FROM drivers WHERE name=? OR (iqama=? AND iqama != \'\')', (name, iqama))
        res = c.fetchone()
        
        if res:
            c.execute('''UPDATE drivers SET empid=?, name=?, iqama=?, job=?, phone=?, plate=?, car=? WHERE id=?''', 
                      (empid, name, iqama, job, phone, plate, car, res[0]))
            updated_count += 1
        else:
            c.execute('''INSERT INTO drivers (empid, name, iqama, job, phone, plate, car) VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                      (empid, name, iqama, job, phone, plate, car))
            inserted_count += 1

    conn.commit()
    conn.close()
    print(f'Sync complete: {updated_count} updated, {inserted_count} inserted.')

if __name__ == '__main__':
    sync_database()
