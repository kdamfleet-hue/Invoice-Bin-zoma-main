import sqlite3
import os

db_path = 'database.sqlite'
if not os.path.exists(db_path):
    print("DB not found")
else:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    for row in cur.fetchall():
        if row[0] in ['drivers', 'erp_drivers', 'erp_branches']:
            print(f"--- {row[0]} ---")
            print(row[1])
