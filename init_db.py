import sqlite3, json, os

folder = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(folder, 'database.sqlite')

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    plate TEXT,
    car TEXT
)
''')

# Check if empty
c.execute('SELECT COUNT(*) FROM drivers')
if c.fetchone()[0] == 0:
    # load from drivers_data.js if possible, or just add some
    js_path = os.path.join(folder, 'drivers_data.js')
    if os.path.exists(js_path):
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
            json_str = content.replace('const driversData = ', '').strip()[:-1]
            try:
                data = json.loads(json_str)
                for d in data:
                    c.execute('INSERT INTO drivers (name, plate, car) VALUES (?, ?, ?)', (d['name'], d['plate'], d['car']))
                print(f"Inserted {len(data)} drivers into DB.")
            except Exception as e:
                print("Error loading JS data:", e)

conn.commit()
conn.close()
print("Database initialized successfully.")



