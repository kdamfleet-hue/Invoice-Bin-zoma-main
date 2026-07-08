import os
import sqlite3
import json
import logging
from contextlib import contextmanager
from flask import current_app

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

logger = logging.getLogger('InvoiceApp')

DATABASE_URL = (os.environ.get('DATABASE_URL') or '').strip()
USE_POSTGRES = bool(DATABASE_URL) and psycopg2 is not None
if DATABASE_URL and psycopg2 is None:
    logger.warning('DATABASE_URL is set but psycopg2 is not installed — falling back to SQLite.')

DB_PATH = os.environ.get('SQLITE_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.sqlite'))

def _translate_sql(sql):
    return sql.replace('?', '%s')

class _PgCursor:
    def __init__(self, cur):
        self._cur = cur

    def execute(self, sql, params=()):
        self._cur.execute(_translate_sql(sql), params)
        return self

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    @property
    def lastrowid(self):
        return None

    def __getattr__(self, name):
        return getattr(self._cur, name)

class _PgConn:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return _PgCursor(self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor))

    def execute(self, sql, params=()):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

def get_db():
    if USE_POSTGRES:
        return _PgConn(psycopg2.connect(DATABASE_URL))
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

@contextmanager
def db_connection():
    conn = get_db()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def _pk_clause():
    return 'SERIAL PRIMARY KEY' if USE_POSTGRES else 'INTEGER PRIMARY KEY AUTOINCREMENT'

def _drivers_table_columns(db):
    if USE_POSTGRES:
        rows = db.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'drivers'"
        ).fetchall()
        return {r['column_name'] for r in rows}
    rows = db.execute('PRAGMA table_info(drivers)').fetchall()
    return {r['name'] for r in rows}

def _is_header_row(d):
    name = (d.get('name') or '').strip()
    if not name:
        return True
    return ('اسم السائق' in name) or ('Employee Name' in name) or ('ID Number' in name)

def init_db(app=None):
    with (app.app_context() if app else current_app.app_context()):
        with db_connection() as db:
            db.execute(
                'CREATE TABLE IF NOT EXISTS drivers ('
                'id %s, name TEXT NOT NULL, empid TEXT, plate TEXT, '
                'car TEXT, iqama TEXT, phone TEXT, drivercard TEXT)' % _pk_clause()
            )
            db.execute('CREATE TABLE IF NOT EXISTS washing_schedule (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS schedule_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS records_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS incidents_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS gps_devices_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS app_users (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS data_snapshots (id %s, tab TEXT, ts TEXT, data TEXT, mode INTEGER)' % _pk_clause())
            db.execute('CREATE TABLE IF NOT EXISTS drivers_ws (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS oils_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS purchase_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS workshop_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS handover_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS drivers_branch (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS branch_accounts (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS alert_settings (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS documents_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS driver_registry (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS vehicle_registry (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS hr_employees (id %s, empid TEXT, iqama TEXT, name TEXT, plate TEXT, phone TEXT, job TEXT, details TEXT)' % _pk_clause())
            db.execute('CREATE TABLE IF NOT EXISTS deauthorized_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS drivers_backup (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS ws_meta (k TEXT PRIMARY KEY, v TEXT)')
            db.commit()

            # Postgres folds unquoted identifiers to lowercase (an ADD COLUMN empNotes really
            # creates "empnotes"), while SQLite's PRAGMA table_info preserves whatever case the
            # column was created with. Compare case-insensitively on both sides so a mixed-case
            # name like empNotes is correctly recognized as already existing on every restart —
            # otherwise this migration re-attempts the ALTER on Postgres every single boot and
            # crashes the whole app with a DuplicateColumn error once the column is there.
            existing_cols = _drivers_table_columns(db)
            existing_cols_lower = {c.lower() for c in existing_cols}
            if 'drivercard' not in existing_cols_lower:
                db.execute('ALTER TABLE drivers ADD COLUMN drivercard TEXT')
                db.commit()
                logger.info('Database Migration: Added drivercard column to drivers table')

            new_cols = [
                'job', 'empNotes', 'model', 'pallets', 'load',
                'vserial', 'inspect', 'license', 'opcard', 'notes',
                'fuel_card', 'medical_exp', 'contract_exp'
            ]
            for col in new_cols:
                if col.lower() not in existing_cols_lower:
                    db.execute(f'ALTER TABLE drivers ADD COLUMN {col} TEXT')
                    db.commit()
                    logger.info(f'Database Migration: Added {col} column to drivers table')

            count = db.execute('SELECT COUNT(*) AS cnt FROM drivers').fetchone()['cnt']
            if count == 0:
                js_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'drivers_data.js')
                if os.path.exists(js_path):
                    try:
                        with open(js_path, 'r', encoding='utf-8') as f:
                            content = f.read().replace('const driversData = ', '').strip()
                            if content.endswith(';'):
                                content = content[:-1]
                            data = json.loads(content)
                        seeded = 0
                        for d in data:
                            if _is_header_row(d):
                                continue
                            db.execute(
                                'INSERT INTO drivers (name, empid, plate, car, iqama, phone, drivercard) '
                                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                                (
                                    d.get('name', ''), d.get('empid', ''), d.get('plate', ''),
                                    d.get('car', ''), d.get('iqama', ''), d.get('phone', ''),
                                    d.get('drivercard', ''),
                                ),
                            )
                            seeded += 1
                        db.commit()
                        logger.info('Database seeded once with %d drivers from drivers_data.js', seeded)
                    except Exception as e:
                        db.rollback()
                        logger.error('Error seeding DB: %s', e)

            db.commit()
    logger.info('Database initialized successfully.')
