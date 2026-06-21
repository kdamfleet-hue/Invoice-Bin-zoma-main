import os
import io
import logging
import shutil
import secrets
import hmac
import openpyxl
from copy import copy
from contextlib import contextmanager
from openpyxl.drawing.image import Image as XLImage
from openpyxl.cell.cell import MergedCell as MC
import sqlite3
import base64
import requests
import json
import re
from functools import wraps

try:
    import psycopg2
    import psycopg2.extras
except ImportError:  # psycopg2 only required when DATABASE_URL (PostgreSQL) is used
    psycopg2 = None
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv
from flask_mail import Mail, Message
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("InvoiceApp")

# Directories
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "user_templates")
try:
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
except PermissionError:
    # Fallback to /tmp for read-only deployment environments (like Render/Heroku)
    TEMPLATE_DIR = "/tmp/user_templates"
    os.makedirs(TEMPLATE_DIR, exist_ok=True)

# ── Database configuration ────────────────────────────────────────────────────
# Production (ArabCord/Render) provides a PostgreSQL DATABASE_URL → use it (persistent).
# Locally / when unset → use a SQLite file at a PERSISTENT path (never /tmp, which is wiped).
DATABASE_URL = (os.environ.get("DATABASE_URL") or "").strip()
USE_POSTGRES = bool(DATABASE_URL) and psycopg2 is not None
if DATABASE_URL and psycopg2 is None:
    logger.warning("DATABASE_URL is set but psycopg2 is not installed — falling back to SQLite.")

# SQLite path (used only when no PostgreSQL). Configurable, persistent by default.
DB_PATH = os.environ.get(
    "SQLITE_PATH", os.path.join(os.path.dirname(__file__), "database.sqlite")
)

LOGO_PATH = os.path.join(os.path.dirname(__file__), "static", "excel_logo.png")

# Valid tab names for template upload
VALID_TABS = {"invoice", "oils", "purchase", "schedule", "workshop"}
# Default template filenames (fallback)
DEFAULT_TEMPLATES = {
    "oils": "oils_template.xlsx",
    "purchase": "po_template.xlsx",
    "schedule": "schedule_base.xlsx",
    "workshop": "تقرير الورشة.xlsx",
}

# Logo for email headers (120x80px PNG, white bg)
EMAIL_LOGO_B64 = "iVBORw0KGgoAAAANSUhEUgAAAHgAAABQCAIAAABd+SbeAAAGl0lEQVR42u3abWybVxUH8HPu47eSxHFiu3GTKW5e3KR5aZhDOkqmFhoxadpg0wqCIugEqwZsIAqIicKmdqNiCLURQhvdBmXVVrUrRJ3WoWpsq1iaboNuTZs0IU7avGyu06RJ7Dh+t597Dx9cYOpgdBMTj9H5f/AXPx8e/XR17z3nPEhEwPnwI5iAoRmaw9AMzdAchmZoDkMzNENzGJqhOQzN0AzNYWiG5jA0QzM0h6HfHQIoxMG9KDhlBEAsPOtCgiYCBFBSZbKy4KxFgRBfSSSWvXv30Bd2nLkcTuetlSKG/q8FERFRCBydSvyud/6lM9ETZ+elVAgkBKpCWNto5E/CpCQCQIS3Q3PBS5elpMrlJSeH0WTCdp996+4Rq0176M7aDX6XLsmkIUN/0B0ZAQAy6fjQ6CQRIUJOV6V2ezyRtpcsOztp3dodKCvW9t/XtPFjbqlIE8jQ748YABDh0Iuh8JIOoABRE6jrZC/Suq63DQTGE8ncuraVpyfMW7sDVjM++YOmT691KyKByNDXfE1WJAQ++OT53b+/mEgrRKT8HwCU1e+8ecXOLZ/j8RCqd+3ibdzSobXtsXCD17GjtaCqjIhKGXNcmoykDgRC4c9/57mdDFQ7L5o3L7RbUpcqfiELgXCQdnBfr/I19b4y8PjD1qY762ztde/8wPTQZX9tcpkuGvrZrHADs2j/e/WzIvkzs+UbdWp89GVpwOoob6uuuerhrnfNLfYOXw3GzSWgCgWQmk7JalxtzZLB6BGOJ3OHeuZsJn97W2FKdOX5qvNJdmiXHZ3/Yn0rpRCQQzSbNSfedz9RvWrg5HokpmgEApGApc8HiqqirK/3GQMvS/hhYCECGdzj3+3cZWb6avf8LjdGy4oXlkKnv8bPTSg5PxZzKS9p1LHZX/YeKDnw4xeVIkRFSORKZ2EkT8Kkz0N/ZGbB41DY3VNyc3+8upC7MlMRKZKV6EjOE2vk6xK2z7yeEMPlugbpoCdAzDdqdKnvnd49AQBgt9u1Df2Ct1gsqizLeNovNhp0+C2OA8koaQnp9/rO2/aKxSaD7qM0c2S9LTfqSPVL+g7gdLk3R4Lvn7+mOzy/opoQygzl5NQIq0/p5lhK0e2LzTzqGkWc+MfHZXRCoZDRfINvaOwiz6hElTDSJI1SP3BSkjGC9pRbIp/87qt+t6PBqkEYVgcUzn9CAABxl/mB7nH0vYi07reLMYozcWJtqzI2u8KnIVC0eTcdVgg//uLewJtFRfvcQCkKR1Bh/zeUZYrtdqSVVnXmdI4JjvQEzWUyIPV+s7p1f5Zk8HkDQ5a8h0/4lTsdTtiCWifdzGoFQylFZ2t+TNl1tN2TVdJW99ddpChfbuVZGXiXku/4WVeK/MlA9GqOFK+HGgnWaVXKgvnXjSkLjWEYhmEYhmEYhmEYhmH+sz8BzQDdMcl1yrQAAAAASUVORK5CYII="

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
_secret = os.environ.get("SECRET_KEY")
if not _secret:
    # No hardcoded fallback key (that would let anyone forge sessions).
    # Generate a strong ephemeral key so the app still runs; warn loudly.
    _secret = secrets.token_hex(32)
    logger.warning(
        "SECRET_KEY not set — generated a random ephemeral key. "
        "Sessions will reset on restart. Set SECRET_KEY in the environment for production!"
    )
app.secret_key = _secret

# CORS: the app serves its own same-origin frontend, so cross-origin is disabled by
# default. Set ALLOWED_ORIGINS (comma-separated) only if external clients are needed.
_allowed_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()]
if _allowed_origins:
    CORS(app, resources={r"/api/*": {"origins": _allowed_origins}}, supports_credentials=True)

# Harden the session cookie
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_DEBUG", "False").lower() != "true"

# Session lifetime: 8 hours
from datetime import timedelta

app.permanent_session_lifetime = timedelta(hours=8)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# Security Decorator (defined early so it is available to all routes below)
WS_PREFIX = "/importantworkstation"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # The /importantworkstation/* namespace is an OPEN, separate workstation — no main login.
        if request.path.startswith(WS_PREFIX):
            return f(*args, **kwargs)
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function

# ── GPS Configuration ────────────────────────────────────────────────────────
GPS_USER = os.environ.get("GPS_USER", "")
GPS_PASS = os.environ.get("GPS_PASS", "")
# Default to the actual JSON API endpoint (NOT the web-UI SPA URL which returns HTML).
GPS_ASSET_URL = os.environ.get(
    "GPS_ASSET_URL", "https://fleetmanagement-api-clust03.gpscockpit.com/api/asset"
)
# Accept either GPS_TOKEN (ArabCord) or the legacy GPS_PERMANENT_TOKEN name.
GPS_PERMANENT_TOKEN = os.environ.get("GPS_TOKEN") or os.environ.get("GPS_PERMANENT_TOKEN", "")


def get_gps_token():
    """Return the GPS API token from environment."""
    return GPS_PERMANENT_TOKEN


logger.info("Starting Fleet Management System...")
logger.info("Template Dir: %s", TEMPLATE_DIR)
logger.info("Database Path: %s", DB_PATH)


@app.route("/health")
def health():
    return jsonify(
        {"status": "healthy", "env": "Render" if os.environ.get("RENDER") else "Local"}
    )


@app.route("/api/gps")
@login_required
def get_gps_locations():
    token = get_gps_token()
    if not token:
        return (
            jsonify(
                {"error": "خدمة التتبع غير مهيأة — لم يتم ضبط مفتاح GPS (GPS_TOKEN)."}
            ),
            503,
        )

    headers = {
        "Authorization": f"GpsCockpitApiKey {token}",
        "Accept": "application/json",
    }
    try:
        response = requests.get(GPS_ASSET_URL, headers=headers, timeout=20)
        if response.status_code != 200:
            # Do NOT echo provider body to the client (may leak internals); log it instead.
            logger.warning("GPS API non-200 %s: %s", response.status_code, response.text[:300])
            return (
                jsonify({"error": "تعذّر جلب بيانات GPS من المزوّد حالياً."}),
                502,
            )
        # Guard against HTML responses (e.g. misconfigured URL pointing at the web UI).
        ctype = response.headers.get("Content-Type", "")
        if "application/json" not in ctype:
            logger.warning("GPS API returned non-JSON (%s). Check GPS_ASSET_URL.", ctype)
            return (
                jsonify({"error": "استجابة GPS غير صالحة — تأكد من ضبط GPS_ASSET_URL على نقطة API."}),
                502,
            )
        return jsonify(response.json())
    except requests.Timeout:
        return jsonify({"error": "تجاوز وقت الاستجابة من خدمة GPS."}), 504
    except requests.ConnectionError:
        return jsonify({"error": "تعذّر الاتصال بخدمة GPS."}), 503
    except Exception as e:
        logger.error("GPS API error: %s", e)
        return jsonify({"error": "حدث خطأ غير متوقع أثناء جلب بيانات GPS."}), 500


# Flask-Mail Configuration
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
mail = Mail(app)

# OAuth configuration removed


def _translate_sql(sql):
    """Translate SQLite-style '?' placeholders to PostgreSQL-style '%s'."""
    return sql.replace("?", "%s")


class _PgCursor:
    """Cursor wrapper so PostgreSQL behaves like sqlite3 (rows are dict-like)."""

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
        return None  # PostgreSQL: use 'RETURNING id' instead

    def __getattr__(self, name):
        return getattr(self._cur, name)


class _PgConn:
    """Connection wrapper exposing the same surface the app uses on sqlite3."""

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
    """Open a database connection (PostgreSQL in production, else SQLite). Rows are dict-like."""
    if USE_POSTGRES:
        return _PgConn(psycopg2.connect(DATABASE_URL))
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrency
    return conn


@contextmanager
def db_connection():
    """Context manager that guarantees DB connection cleanup."""
    conn = get_db()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _pk_clause():
    """Portable auto-increment primary key clause."""
    return "SERIAL PRIMARY KEY" if USE_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"


def _drivers_table_columns(db):
    """Return the set of column names on the drivers table (portable)."""
    if USE_POSTGRES:
        rows = db.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'drivers'"
        ).fetchall()
        return {r["column_name"] for r in rows}
    rows = db.execute("PRAGMA table_info(drivers)").fetchall()
    return {r["name"] for r in rows}


def _is_header_row(d):
    """True for the junk header rows present in drivers_data.js (must not be seeded)."""
    name = (d.get("name") or "").strip()
    if not name:
        return True
    return ("اسم السائق" in name) or ("Employee Name" in name) or ("ID Number" in name)


def init_db():
    """Create tables if missing and seed drivers ONCE. Never destructive (no data loss)."""
    with app.app_context():
        with db_connection() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS drivers ("
                "id %s, name TEXT NOT NULL, empid TEXT, plate TEXT, "
                "car TEXT, iqama TEXT, phone TEXT, drivercard TEXT)" % _pk_clause()
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS washing_schedule (id INTEGER PRIMARY KEY, data TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, data TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS schedule_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS records_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)"
            )
            # Workstation-only blob stores (id=2 sandbox). Additive & never seeded, so the
            # /importantworkstation namespace starts EMPTY and persists what the user types.
            # The MAIN site (/) never reads or writes these.
            db.execute(
                "CREATE TABLE IF NOT EXISTS drivers_ws (id INTEGER PRIMARY KEY, data TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS oils_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS purchase_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS workshop_data (id INTEGER PRIMARY KEY, data TEXT NOT NULL)"
            )
            # Tiny key/value flags for the workstation (e.g. "did we auto-seed example data?").
            db.execute(
                "CREATE TABLE IF NOT EXISTS ws_meta (k TEXT PRIMARY KEY, v TEXT)"
            )
            db.commit()

            # Safe migration: add drivercard to older tables that lack it.
            if "drivercard" not in _drivers_table_columns(db):
                db.execute("ALTER TABLE drivers ADD COLUMN drivercard TEXT")
                db.commit()
                logger.info("Database Migration: Added drivercard column to drivers table")

            # Seed drivers ONCE, only when the table is completely empty.
            # We never DELETE existing rows — that previously wiped user-added drivers on every restart.
            count = db.execute("SELECT COUNT(*) AS cnt FROM drivers").fetchone()["cnt"]
            if count == 0:
                js_path = os.path.join(app.root_path, "drivers_data.js")
                if os.path.exists(js_path):
                    try:
                        with open(js_path, "r", encoding="utf-8") as f:
                            content = f.read().replace("const driversData = ", "").strip()
                            if content.endswith(";"):
                                content = content[:-1]
                            data = json.loads(content)
                        seeded = 0
                        for d in data:
                            if _is_header_row(d):
                                continue
                            db.execute(
                                "INSERT INTO drivers (name, empid, plate, car, iqama, phone, drivercard) "
                                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (
                                    d.get("name", ""), d.get("empid", ""), d.get("plate", ""),
                                    d.get("car", ""), d.get("iqama", ""), d.get("phone", ""),
                                    d.get("drivercard", ""),
                                ),
                            )
                            seeded += 1
                        db.commit()
                        logger.info("Database seeded once with %d drivers from drivers_data.js", seeded)
                    except Exception as e:
                        db.rollback()
                        logger.error("Error seeding DB: %s", e)

            db.commit()
    logger.info("Database initialized successfully.")

init_db()


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("authenticated"):
        return redirect(url_for("index"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        master_user = os.environ.get("ADMIN_USERNAME", "admin")
        master_pass = os.environ.get("MASTER_PASSWORD")

        if not master_pass:
            logger.error("MASTER_PASSWORD environment variable is not set!")
            return render_template("login.html", error="خطأ في إعداد النظام. يرجى التواصل مع المدير.")

        # Constant-time comparison; only the configured ADMIN_USERNAME is accepted.
        user_ok = hmac.compare_digest(username, master_user)
        pass_ok = hmac.compare_digest(password, master_pass)
        if user_ok and pass_ok:
            session["authenticated"] = True
            session.permanent = True
            session["google_user"] = {"name": username, "email": "admin@system.local"}
            logger.info("Successful login")
            return redirect(url_for("index"))
        else:
            logger.warning("Failed login attempt")
            return render_template("login.html", error="اسم المستخدم أو كلمة المرور غير صحيحة")

    return render_template("login.html")


# ── Workstation namespace (/importantworkstation/*) ───────────────────────────
# A COMPLETELY SEPARATE, OPEN entry that mirrors the site under a URL prefix. It is a
# sandbox (edits go to id=2, never touching the real id=1 data) and the
# Cameras/Employees/GPS-Sync tabs are password-locked. The MAIN site (/) is untouched.
WORKSTATION_PASSWORD = os.environ.get("WORKSTATION_PASSWORD", "Kn-123123")
WS_TABS = {
    "": "index", "schedule": "schedule", "oils": "oils", "purchase": "purchase",
    "washing": "washing", "workshop": "workshop", "search": "search", "records": "records",
    "tracking": "tracking", "employees": "employees", "gps_sync": "gps_sync", "cameras": "cameras",
}
WS_LOCKED = {"employees", "gps_sync", "cameras", "tracking"}


def is_workstation():
    """Determined purely by the URL prefix — never by the session — so the main site is
    never affected, even in the same browser."""
    return request.path.startswith(WS_PREFIX)


def _row_id():
    return 2 if is_workstation() else 1


def blob_get(table):
    """Read a single-row JSON blob.
    Main site reads id=1. The workstation reads ONLY its own id=2 sandbox and NEVER
    falls back to id=1 — so /importantworkstation starts EMPTY instead of mirroring the
    real site's data."""
    rid = _row_id()
    with db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT data FROM %s WHERE id = ?" % table, (rid,))
        row = c.fetchone()
        if not row and rid != 1 and not is_workstation():
            c.execute("SELECT data FROM %s WHERE id = 1" % table)
            row = c.fetchone()
    return json.loads(row["data"]) if row else None


def blob_set(table, data_obj):
    """Write a single-row JSON blob to the mode-specific row (id=2 for workstation)."""
    rid = _row_id()
    data_str = json.dumps(data_obj, ensure_ascii=False)
    with db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM %s WHERE id = ?" % table, (rid,))
        if c.fetchone():
            c.execute("UPDATE %s SET data = ? WHERE id = ?" % table, (data_str, rid))
        else:
            c.execute("INSERT INTO %s (id, data) VALUES (?, ?)" % table, (rid, data_str))
        conn.commit()


# ── Workstation example/demo data (FAKE — for the open sandbox only) ──────────
# Loaded once from ws_example_data.json. The MAIN site never touches any of this.
WS_EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), "ws_example_data.json")
try:
    with open(WS_EXAMPLE_PATH, encoding="utf-8") as _wsf:
        WS_EXAMPLE_DATA = json.load(_wsf)
except Exception as _e:
    logger.warning("ws_example_data.json not loaded: %s", _e)
    WS_EXAMPLE_DATA = {}


def _ws_meta_get(k):
    with db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT v FROM ws_meta WHERE k = ?", (k,))
        row = c.fetchone()
    return row["v"] if row else None


def _ws_meta_set(k, v):
    with db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT k FROM ws_meta WHERE k = ?", (k,))
        if c.fetchone():
            c.execute("UPDATE ws_meta SET v = ? WHERE k = ?", (v, k))
        else:
            c.execute("INSERT INTO ws_meta (k, v) VALUES (?, ?)", (k, v))
        conn.commit()


def _ws_get2(table):
    """Read the workstation (id=2) blob for a table, or None."""
    with db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT data FROM %s WHERE id = 2" % table)
        row = c.fetchone()
    return json.loads(row["data"]) if row else None


def _ws_put2(table, value):
    """Upsert the workstation (id=2) blob for a table."""
    data_str = json.dumps(value, ensure_ascii=False)
    with db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM %s WHERE id = 2" % table)
        if c.fetchone():
            c.execute("UPDATE %s SET data = ? WHERE id = 2" % table, (data_str,))
        else:
            c.execute("INSERT INTO %s (id, data) VALUES (2, ?)" % table, (data_str,))
        conn.commit()


def _ws_is_empty(value):
    """True if a stored blob carries NO real rows — covers a missing row, [], {}, and an
    'empty shell' object like {title, date:'', main:[], spare:[], vacation:[], summary:{vacation:'0'}}
    that a stray autosave may have written (this is why a tab can look permanently empty).
    Rows live ONLY in LIST fields (main/spare/vacation/oils/filters/parts/…); scalar and dict
    fields (title, date, summary) are metadata and never count as data."""
    if value is None:
        return True
    if isinstance(value, list):
        return len(value) == 0
    if isinstance(value, dict):
        for v in value.values():
            if isinstance(v, list) and len(v) > 0:
                return False
        return True  # no non-empty list field → no rows
    return False


def _ws_write_examples():
    """Overwrite ALL workstation id=2 stores with the FAKE example data (used by 🧪)."""
    for table, value in WS_EXAMPLE_DATA.items():
        _ws_put2(table, value)


def ensure_ws_seeded():
    """Self-healing seed: on every workstation page load, fill any store that is EMPTY
    (missing OR an empty/empty-shell blob) from the example data, while PRESERVING any store
    that holds real rows the user typed. Skipped entirely if the user emptied the sandbox with
    the 🗑️ button (ws_cleared flag), so a deliberate reset stays empty."""
    try:
        if _ws_meta_get("ws_cleared") == "1":
            return
        for table, value in WS_EXAMPLE_DATA.items():
            if _ws_is_empty(_ws_get2(table)):
                _ws_put2(table, value)
    except Exception:
        logger.exception("ensure_ws_seeded error")


@app.route(WS_PREFIX)
@app.route(WS_PREFIX + "/<path:sub>")
def workstation_page(sub=""):
    """Open workstation pages under the prefix. The 3 sensitive tabs require the password."""
    ensure_ws_seeded()  # first visit fills the sandbox with fake example data
    seg = sub.strip("/").split("/")[0] if sub else ""
    if seg == "api":
        return ("", 404)  # API served by the mirrored /importantworkstation/api/* rules
    if seg not in WS_TABS:
        return redirect(WS_PREFIX)
    if seg in WS_LOCKED and not session.get("ws_unlocked"):
        return render_template("tab_lock.html", next=WS_PREFIX + "/" + seg)
    ctx = {"google_user": {"name": "Workstation", "email": "ws@system.local"}, "b64_en": load_logo()}
    if seg == "cameras":
        ctx["cameras_url"] = os.environ.get("CAMERAS_URL", "")
    return render_template(WS_TABS[seg] + ".html", **ctx)


@app.route(WS_PREFIX + "/unlock", methods=["POST"])
def workstation_unlock():
    nxt = request.form.get("next", WS_PREFIX)
    if not nxt.startswith(WS_PREFIX):
        nxt = WS_PREFIX
    if hmac.compare_digest(request.form.get("password", ""), WORKSTATION_PASSWORD):
        session["ws_unlocked"] = True
        resp = redirect(nxt)
        resp.set_cookie("ws_unlocked", "1", path=WS_PREFIX, samesite="Lax",
                        secure=app.config.get("SESSION_COOKIE_SECURE", False))
        return resp
    return render_template("tab_lock.html", next=nxt, error="كلمة المرور غير صحيحة")


@app.route("/logout")
def logout():
    session.clear()
    resp = redirect(url_for("login"))
    resp.delete_cookie("ws_unlocked", path=WS_PREFIX)
    return resp


@app.route("/tracking")
@login_required
def tracking_page():
    return render_template("tracking.html")


def load_logo():
    b64_en = ""
    txt_path = os.path.join(app.root_path, "b64.txt")
    if os.path.exists(txt_path):
        with open(txt_path, "r") as f:
            content = f.read().strip()
            if not content.startswith("ar='") and not content.startswith("en='"):
                b64_en = content
    return b64_en


@app.route("/")
@login_required
def index():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("index.html", google_user=google_user, b64_en=b64_en)


@app.route("/oils")
@login_required
def oils():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("oils.html", google_user=google_user, b64_en=b64_en)


@app.route("/purchase")
@login_required
def purchase():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("purchase.html", google_user=google_user, b64_en=b64_en)


@app.route("/schedule")
@login_required
def schedule():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("schedule.html", google_user=google_user, b64_en=b64_en)


@app.route("/washing")
@login_required
def washing():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("washing.html", google_user=google_user, b64_en=b64_en)

@app.route("/employees")
@login_required
def employees():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("employees.html", google_user=google_user, b64_en=b64_en)


@app.route("/gps_sync")
@login_required
def gps_sync():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("gps_sync.html", google_user=google_user, b64_en=b64_en)


@app.route("/workshop")
@login_required
def workshop():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("workshop.html", google_user=google_user, b64_en=b64_en)


@app.route("/search")
@login_required
def search_page():
    return render_template("search.html", google_user=session.get("google_user"), b64_en=load_logo())


@app.route("/records")
@login_required
def records_page():
    return render_template("records.html", google_user=session.get("google_user"), b64_en=load_logo())


@app.route("/cameras")
@login_required
def cameras_page():
    # Embeds Hik-Connect in an iframe. URL is configurable via the CAMERAS_URL env var
    # (or per-browser in the UI). Note: Hik-Connect may block iframing (X-Frame-Options).
    return render_template(
        "cameras.html",
        google_user=session.get("google_user"),
        b64_en=load_logo(),
        cameras_url=os.environ.get("CAMERAS_URL", ""),
    )


@app.route("/api/vehicles_lookup")
@login_required
def vehicles_lookup():
    """Serve the vehicle/driver registry (authenticated — contains personal data)."""
    path = os.path.join(app.root_path, "vehicles_lookup.json")
    if not os.path.exists(path):
        return jsonify([])
    try:
        with open(path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception:
        logger.exception("vehicles_lookup read error")
        return jsonify([])


@app.route("/api/download_workshop_template")
@login_required
def download_workshop_template():
    """Download the workshop report Excel template."""
    from flask import send_file
    template_path = os.path.join(os.path.dirname(__file__), "تقرير الورشة.xlsx")
    if not os.path.exists(template_path):
        return jsonify({"error": "قالب تقرير الورشة غير موجود"}), 404
    return send_file(template_path, as_attachment=True, download_name="تقرير_الورشة.xlsx")


# ─── Template Upload & Management ─────────────────────────────
def get_template_path(tab):
    """Return path to user-uploaded template, or default template fallback."""
    user_path = os.path.join(TEMPLATE_DIR, f"{tab}_template.xlsx")
    if os.path.exists(user_path):
        return user_path
    default_name = DEFAULT_TEMPLATES.get(tab)
    if default_name:
        default_path = os.path.join(os.path.dirname(__file__), default_name)
        if os.path.exists(default_path):
            return default_path
    return None


def inject_logo(ws, cell="A1"):
    """Insert company logo into worksheet if logo file exists."""
    if os.path.exists(LOGO_PATH):
        try:
            img = XLImage(LOGO_PATH)
            img.width = 500
            img.height = 120
            ws.add_image(img, cell)
        except Exception:
            pass


MAX_TEMPLATE_SIZE = 16 * 1024 * 1024  # 16 MB


@app.route("/api/upload_template/<tab>", methods=["POST"])
@login_required
def upload_template(tab):
    if tab not in VALID_TABS:
        return jsonify({"error": "Invalid tab name"}), 400
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    if not f.filename or not f.filename.lower().endswith(".xlsx"):
        return jsonify({"error": "Only .xlsx files allowed"}), 400
    # Check file size
    f.seek(0, 2)
    size = f.tell()
    f.seek(0)
    if size > MAX_TEMPLATE_SIZE:
        return jsonify({"error": "File size exceeds 16MB limit"}), 413
    safe_name = secure_filename(f.filename)
    dest = os.path.join(TEMPLATE_DIR, f"{tab}_template.xlsx")
    f.save(dest)
    logger.info("Template uploaded for tab '%s': %s (%d bytes)", tab, safe_name, size)
    return jsonify({"success": True, "tab": tab, "filename": safe_name})


@app.route("/api/templates", methods=["GET"])
@login_required
def list_templates():
    result = {}
    for tab in VALID_TABS:
        user_path = os.path.join(TEMPLATE_DIR, f"{tab}_template.xlsx")
        result[tab] = {"has_custom": os.path.exists(user_path)}
    return jsonify(result)


@app.route("/api/delete_template/<tab>", methods=["DELETE"])
@login_required
def delete_template(tab):
    if tab not in VALID_TABS:
        return jsonify({"error": "Invalid tab"}), 400
    user_path = os.path.join(TEMPLATE_DIR, f"{tab}_template.xlsx")
    if os.path.exists(user_path):
        os.remove(user_path)
    return jsonify({"success": True})


# ─── Generate Invoice (Server-Side) ──────────────────────────
@app.route("/api/generate_invoice", methods=["POST"])
@login_required
def generate_invoice():
    try:
        data = request.json
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.sheet_view.rightToLeft = True
        ws.title = "فاتورة"

        # Check for custom template
        tpl_path = get_template_path("invoice")
        if tpl_path:
            wb = openpyxl.load_workbook(tpl_path)
            ws = wb.active
        else:
            # Build simple professional invoice from scratch
            from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

            P = "0C2340"
            thin = Side(style="thin", color=P)
            border = Border(top=thin, bottom=thin, left=thin, right=thin)

            # Logo area
            ws.merge_cells("A1:G3")
            inject_logo(ws, "A1")

            # Title
            ws.merge_cells("A4:G4")
            ws["A4"] = "فاتورة صيانة مركبة"
            ws["A4"].font = Font(name="Arial", size=16, bold=True, color=P)
            ws["A4"].alignment = Alignment(horizontal="center", vertical="center")

            # Info fields
            info = [
                ("A5", "اسم السائق:", "B5", data.get("driver", "")),
                ("D5", "التاريخ:", "E5", data.get("date", "")),
                ("A6", "نوع السيارة:", "B6", data.get("car", "")),
                ("D6", "رقم اللوحة:", "E6", data.get("plate", "")),
                ("A7", "نوع الطلب:", "B7", data.get("requestType", "")),
            ]
            for lbl_cell, lbl, val_cell, val in info:
                ws[lbl_cell] = lbl
                ws[lbl_cell].font = Font(name="Arial", size=11, bold=True, color=P)
                ws[val_cell] = val
                ws[val_cell].font = Font(name="Arial", size=11)

            # Table header
            headers = ["م", "الوصف", "الكمية", "السعر", "المبلغ"]
            for i, h in enumerate(headers):
                c = ws.cell(row=9, column=i + 1, value=h)
                c.font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
                c.fill = PatternFill("solid", fgColor=P)
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.border = border

            # Data row
            qty = float(data.get("quantity", 0) or 0)
            price = float(data.get("price", 0) or 0)
            subtotal = qty * price
            row_data = [1, data.get("description", ""), qty, price, subtotal]
            for i, v in enumerate(row_data):
                c = ws.cell(row=10, column=i + 1, value=v)
                c.font = Font(name="Arial", size=11)
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.border = border

            # Totals
            tax = subtotal * 0.15
            total = subtotal + tax
            for ri, (lbl, val) in enumerate(
                [
                    ("المبلغ الإجمالي (قبل الضريبة)", subtotal),
                    ("ضريبة القيمة المضافة (15%)", tax),
                    ("المجموع الكلي (مع الضريبة)", total),
                ]
            ):
                r = 11 + ri
                ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
                ws.cell(row=r, column=1, value=lbl).font = Font(
                    name="Arial", size=11, bold=True, color=P
                )
                ws.cell(row=r, column=5, value=val).font = Font(
                    name="Arial", size=12, bold=(ri == 2), color=P
                )

            # Signatures
            ws.cell(row=15, column=1, value="توقيع السائق").font = Font(
                name="Arial", bold=True, color=P
            )
            ws.cell(row=15, column=5, value="اعتماد الإدارة").font = Font(
                name="Arial", bold=True, color=P
            )

            # Column widths
            for col, w in [
                (1, 8),
                (2, 30),
                (3, 12),
                (4, 12),
                (5, 15),
                (6, 12),
                (7, 12),
            ]:
                ws.column_dimensions[chr(64 + col)].width = w

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode("utf-8")
        driver = data.get("driver", "").replace(" ", "_")[:20]
        plate = data.get("plate", "").replace(" ", "_")[:15]
        fname = f"فاتورة_{driver}_{plate}.xlsx"
        return jsonify({"success": True, "file_b64": b64, "filename": fname})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/generate_schedule", methods=["POST"])
@login_required
def generate_schedule():
    try:
        data = request.json
        template_path = os.path.join(app.root_path, "schedule_base.xlsx")

        if not os.path.exists(template_path):
            return (
                jsonify({"success": False, "error": "Schedule template not found"}),
                500,
            )

        wb = openpyxl.load_workbook(template_path)
        ws = wb.active

        def safe_set(sheet, row, col, val):
            cell = sheet.cell(row=row, column=col)
            if not isinstance(cell, MC):
                cell.value = val

        # Set date in row 6 col 1
        schedule_date = data.get("date", "")
        safe_set(ws, 6, 1, schedule_date)

        main_data = data.get("main", [])
        spare_data = data.get("spare", [])

        # We need to write from bottom up or just write all and delete rows from bottom up

        # 1. Summary Block (Row 53)
        dina = sum(1 for d in main_data if "دينا" in d.get("type", ""))
        lorry = sum(1 for d in main_data if "لوري" in d.get("type", ""))
        delivery = sum(1 for d in main_data if d.get("job", "") == "موصل")
        dist = sum(1 for d in main_data if d.get("job", "") == "موزع")

        safe_set(ws, 53, 2, len(main_data))
        safe_set(ws, 53, 3, dina)
        safe_set(ws, 53, 4, lorry)
        safe_set(ws, 53, 5, delivery)
        safe_set(ws, 53, 6, dist)
        safe_set(ws, 53, 7, len(spare_data))

        # 2. Spare Data (Row 42-49)
        for idx, rd in enumerate(spare_data[:8]):
            r = 42 + idx
            safe_set(ws, r, 1, idx + 1)
            safe_set(ws, r, 2, rd.get("empid", ""))
            safe_set(ws, r, 3, rd.get("name", ""))
            safe_set(ws, r, 4, rd.get("iqama", ""))
            safe_set(ws, r, 6, rd.get("plate", ""))
            safe_set(ws, r, 8, rd.get("typemodel", ""))
            safe_set(ws, r, 9, rd.get("pallets", ""))
            safe_set(ws, r, 10, rd.get("capacity", ""))
            safe_set(ws, r, 16, rd.get("notes", ""))
            safe_set(ws, r, 17, rd.get("phone", ""))

        # 3. Main Data (Row 9-36)
        for idx, rd in enumerate(main_data[:28]):
            r = 9 + idx
            safe_set(ws, r, 1, idx + 1)
            safe_set(ws, r, 2, rd.get("empid", ""))
            safe_set(ws, r, 3, rd.get("name", ""))
            safe_set(ws, r, 4, rd.get("iqama", ""))
            safe_set(ws, r, 5, rd.get("job", ""))
            safe_set(ws, r, 6, rd.get("plate", ""))
            safe_set(ws, r, 7, rd.get("model", ""))
            safe_set(ws, r, 8, rd.get("type", ""))
            safe_set(ws, r, 9, rd.get("pallets", ""))
            safe_set(ws, r, 10, rd.get("capacity", ""))
            safe_set(ws, r, 11, rd.get("serial", ""))
            safe_set(ws, r, 12, rd.get("inspect", ""))
            safe_set(ws, r, 13, rd.get("license", ""))
            safe_set(ws, r, 14, rd.get("drivercard", ""))
            safe_set(ws, r, 15, rd.get("opcard", ""))
            safe_set(ws, r, 16, rd.get("notes", ""))
            safe_set(ws, r, 17, rd.get("phone", ""))

        # Delete unused rows from bottom up to avoid shifting index bugs
        spare_deletions = 8 - len(spare_data) if len(spare_data) < 8 else 0
        main_deletions = 28 - len(main_data) if len(main_data) < 28 else 0

        if spare_deletions > 0:
            ws.delete_rows(42 + len(spare_data), spare_deletions)
        if main_deletions > 0:
            ws.delete_rows(9 + len(main_data), main_deletions)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode("utf-8")
        return jsonify({"success": True, "file_b64": b64})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/generate_washing", methods=["POST"])
@login_required
def generate_washing():
    try:
        data = request.json
        vehicles = data.get("vehicles", [])

        template_path = os.path.join(app.root_path, "washing_template.xlsx")
        if not os.path.exists(template_path):
            return (
                jsonify({"success": False, "error": "Washing template not found"}),
                500,
            )

        wb = openpyxl.load_workbook(template_path)
        ws = wb.active

        # Insert Logo
        logo_path = os.path.join(
            app.root_path, "templates", "ApplicationFrameHost_KUIZUuJ46O (1).png"
        )
        if os.path.exists(logo_path):
            img = XLImage(logo_path)
            img.width = 300
            img.height = 90
            ws.add_image(img, "F1")

        # Unmerge ALL merged cells to avoid MergedCell write errors
        merged_ranges = list(ws.merged_cells.ranges)
        for mr in merged_ranges:
            ws.unmerge_cells(str(mr))

        # Copy header style from row 4 for reuse
        from copy import copy as shallow_copy
        header_fills = {}
        header_fonts = {}
        header_aligns = {}
        header_borders = {}
        for c in range(1, 19):
            cell = ws.cell(row=4, column=c)
            header_fills[c] = shallow_copy(cell.fill)
            header_fonts[c] = shallow_copy(cell.font)
            header_aligns[c] = shallow_copy(cell.alignment)
            header_borders[c] = shallow_copy(cell.border)

        # Copy a data row style (row 5) for styling data rows
        data_fills = {}
        data_fonts = {}
        data_aligns = {}
        data_borders = {}
        for c in range(1, 19):
            cell = ws.cell(row=5, column=c)
            data_fills[c] = shallow_copy(cell.fill)
            data_fonts[c] = shallow_copy(cell.font)
            data_aligns[c] = shallow_copy(cell.alignment)
            data_borders[c] = shallow_copy(cell.border)

        # Write vehicle data starting at row 5
        for idx, v in enumerate(vehicles):
            r = 5 + idx
            ws.cell(row=r, column=1, value=v.get("id", idx + 1))
            ws.cell(row=r, column=2, value=v.get("plate", ""))
            ws.cell(row=r, column=3, value=v.get("type", ""))
            ws.cell(row=r, column=4, value=v.get("driver", ""))
            months = v.get("m", [])
            total = sum(months)
            for m_idx in range(12):
                val = "استلم" if m_idx < len(months) and months[m_idx] == 1 else None
                ws.cell(row=r, column=5 + m_idx, value=val)
            ws.cell(row=r, column=17, value=total)
            # Apply data styling
            for c in range(1, 19):
                cell = ws.cell(row=r, column=c)
                cell.fill = shallow_copy(data_fills.get(c, data_fills[1]))
                cell.font = shallow_copy(data_fonts.get(c, data_fonts[1]))
                cell.alignment = shallow_copy(data_aligns.get(c, data_aligns[1]))
                cell.border = shallow_copy(data_borders.get(c, data_borders[1]))

        # Summary row: right after last vehicle
        summary_row = 5 + len(vehicles)
        ws.cell(row=summary_row, column=1, value="إجمالي الغسيل الشهري")
        ws.merge_cells(start_row=summary_row, start_column=1, end_row=summary_row, end_column=4)
        for m_idx in range(12):
            col = 5 + m_idx
            start_cell = ws.cell(row=5, column=col).coordinate.replace("5", "")
            formula = '=COUNTIF(%s5:%s%d,"استلم")' % (start_cell, start_cell, summary_row - 1)
            ws.cell(row=summary_row, column=col, value=formula)
        ws.cell(row=summary_row, column=17, value="=SUM(Q5:Q%d)" % (summary_row - 1))

        # Style summary row bold
        from openpyxl.styles import Font, PatternFill, Alignment
        summary_font = Font(name="Cairo", size=11, bold=True, color="FFFFFF")
        summary_fill = PatternFill(start_color="1A3A5C", end_color="1A3A5C", fill_type="solid")
        summary_align = Alignment(horizontal="center", vertical="center")
        for c in range(1, 19):
            cell = ws.cell(row=summary_row, column=c)
            cell.font = summary_font
            cell.fill = summary_fill
            cell.alignment = summary_align

        # Footer row
        footer_row = summary_row + 2
        ws.cell(row=footer_row, column=1, value="تم إعداد هذا الجدول بواسطة قسم الحركة - فرع الدمام")
        ws.merge_cells(start_row=footer_row, start_column=1, end_row=footer_row, end_column=18)

        # Re-merge header rows
        ws.merge_cells("A1:R1")
        ws.merge_cells("A2:D2")
        ws.merge_cells("A3:R3")

        # Update total washes in header
        total_washes = sum(sum(v.get("m", [])) for v in vehicles)
        ws.cell(row=2, column=12, value=total_washes)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode("utf-8")
        return jsonify({"success": True, "file_b64": b64})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/washing_data", methods=["GET", "POST"])
@login_required
def washing_data():
    # Workstation mode writes/reads an isolated copy (id=2); the real data (id=1) is untouched.
    if request.method == "POST":
        try:
            blob_set("washing_schedule", (request.json or {}).get("vehicles", []))
            return jsonify({"success": True})
        except Exception:
            logger.exception("washing_data POST error")
            return jsonify({"success": False, "error": "تعذّر حفظ جدول الغسيل."}), 500
    try:
        data = blob_get("washing_schedule")
        if data is not None:
            return jsonify({"success": True, "vehicles": data})
        return jsonify({"success": False, "vehicles": []})
    except Exception:
        logger.exception("washing_data GET error")
        return jsonify({"success": False, "error": "تعذّر جلب جدول الغسيل."}), 500


@app.route("/api/employees", methods=["GET", "POST"])
@login_required
def employees_data():
    """Persist the branch employees grid (array of 46-column string rows). Sandboxed for workstation."""
    if request.method == "POST":
        try:
            blob_set("employees", (request.json or {}).get("rows", []))
            return jsonify({"success": True})
        except Exception:
            logger.exception("employees_data POST error")
            return jsonify({"success": False, "error": "تعذّر حفظ بيانات الموظفين."}), 500
    try:
        data = blob_get("employees")
        return jsonify({"success": True, "rows": data if data is not None else []})
    except Exception:
        logger.exception("employees_data GET error")
        return jsonify({"success": False, "error": "تعذّر جلب بيانات الموظفين."}), 500


@app.route("/api/schedule_data", methods=["GET", "POST"])
@login_required
def schedule_data():
    """Persist the weekly schedule (main/spare/vacation/summary). Sandboxed for workstation."""
    if request.method == "POST":
        try:
            blob_set("schedule_data", request.json or {})
            return jsonify({"success": True})
        except Exception:
            logger.exception("schedule_data POST error")
            return jsonify({"success": False, "error": "تعذّر حفظ الجدول الأسبوعي."}), 500
    try:
        return jsonify({"success": True, "data": blob_get("schedule_data")})
    except Exception:
        logger.exception("schedule_data GET error")
        return jsonify({"success": False, "error": "تعذّر جلب الجدول الأسبوعي."}), 500


@app.route("/api/records", methods=["GET", "POST"])
@login_required
def records_data():
    """Persist the documentation/records log. Sandboxed for workstation."""
    if request.method == "POST":
        try:
            blob_set("records_data", (request.json or {}).get("rows", []))
            return jsonify({"success": True})
        except Exception:
            logger.exception("records_data POST error")
            return jsonify({"success": False, "error": "تعذّر حفظ السجلات."}), 500
    try:
        data = blob_get("records_data")
        return jsonify({"success": True, "rows": data if data is not None else []})
    except Exception:
        logger.exception("records_data GET error")
        return jsonify({"success": False, "rows": []})


# ── Workstation-only tab state (oils / purchase / workshop) ───────────────────
# These tabs have NO server storage on the main site (hardcoded rows + localStorage).
# For the /importantworkstation sandbox they persist a single JSON object on the server
# (id=2 via blob_get/blob_set). On the main site (id=1) these rows stay empty/unused —
# the main pages never POST here, so the main site keeps its original behavior.
@app.route("/api/oils_data", methods=["GET", "POST"])
@login_required
def oils_data():
    if request.method == "POST":
        try:
            blob_set("oils_data", request.json or {})
            return jsonify({"success": True})
        except Exception:
            logger.exception("oils_data POST error")
            return jsonify({"success": False}), 500
    try:
        return jsonify({"success": True, "data": blob_get("oils_data")})
    except Exception:
        logger.exception("oils_data GET error")
        return jsonify({"success": False, "data": None})


@app.route("/api/purchase_data", methods=["GET", "POST"])
@login_required
def purchase_data():
    if request.method == "POST":
        try:
            blob_set("purchase_data", request.json or {})
            return jsonify({"success": True})
        except Exception:
            logger.exception("purchase_data POST error")
            return jsonify({"success": False}), 500
    try:
        return jsonify({"success": True, "data": blob_get("purchase_data")})
    except Exception:
        logger.exception("purchase_data GET error")
        return jsonify({"success": False, "data": None})


@app.route("/api/workshop_data", methods=["GET", "POST"])
@login_required
def workshop_data():
    if request.method == "POST":
        try:
            blob_set("workshop_data", request.json or {})
            return jsonify({"success": True})
        except Exception:
            logger.exception("workshop_data POST error")
            return jsonify({"success": False}), 500
    try:
        return jsonify({"success": True, "data": blob_get("workshop_data")})
    except Exception:
        logger.exception("workshop_data GET error")
        return jsonify({"success": False, "data": None})


# All id=2 stores used by the workstation sandbox. Used by the reset endpoint below.
WS_BLOB_TABLES = [
    "employees", "schedule_data", "washing_schedule", "records_data",
    "drivers_ws", "oils_data", "purchase_data", "workshop_data",
]


@app.route("/api/ws_reset", methods=["POST"])
@login_required
def ws_reset():
    """Wipe EVERY workstation (id=2) store so /importantworkstation starts truly empty.
    Workstation-only: the main site can never reach this (guard + path-based mirror)."""
    if not is_workstation():
        return jsonify({"success": False, "error": "workstation only"}), 404
    try:
        with db_connection() as conn:
            c = conn.cursor()
            for t in WS_BLOB_TABLES:
                c.execute("DELETE FROM %s WHERE id = 2" % t)
            conn.commit()
        _ws_meta_set("ws_cleared", "1")  # user emptied it on purpose → don't auto-reseed
        return jsonify({"success": True})
    except Exception:
        logger.exception("ws_reset error")
        return jsonify({"success": False}), 500


@app.route("/api/ws_seed", methods=["POST"])
@login_required
def ws_seed():
    """Fill EVERY workstation (id=2) store with the FAKE example data (demo).
    Workstation-only: the main site can never reach this."""
    if not is_workstation():
        return jsonify({"success": False, "error": "workstation only"}), 404
    try:
        _ws_write_examples()
        _ws_meta_set("ws_cleared", "0")  # examples are wanted again → allow auto-seed
        return jsonify({"success": True})
    except Exception:
        logger.exception("ws_seed error")
        return jsonify({"success": False}), 500


@app.route("/api/drivers", methods=["GET"])
@login_required
def get_drivers():
    if is_workstation():
        # Workstation: isolated, server-persistent driver list (id=2). Starts EMPTY.
        lst = blob_get("drivers_ws") or []
        lst = sorted(lst, key=lambda d: d.get("id", 0), reverse=True)
        return jsonify(lst)
    with db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM drivers ORDER BY id DESC")
        drivers = [dict(row) for row in c.fetchall()]
    return jsonify(drivers)


def normalize_plate(plate):
    if plate is None:
        return ""
    plate = str(plate)
    plate = re.sub(r"\s+", "", plate)
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    english_digits = "0123456789"
    for a, e in zip(arabic_digits, english_digits):
        plate = plate.replace(a, e)
    digits = "".join(re.findall(r"\d+", plate))
    letters = "".join(re.findall(r"[^\d]+", plate))
    return digits + letters

def tafqeet(amount):
    try:
        amount = float(amount)
    except:
        return ""
    if amount == 0: return "صفر ريال فقط لا غير"
    
    units = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة", "عشرة",
             "أحد عشر", "اثنا عشر", "ثلاثة عشر", "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر"]
    tens = ["", "عشرة", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"]
    hundreds = ["", "مائة", "مائتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة"]
    
    def convert_999(n):
        if n == 0: return ""
        h = n // 100
        rem = n % 100
        words = []
        if h > 0:
            words.append(hundreds[h])
        if rem > 0:
            if rem < 20:
                words.append(units[rem])
            else:
                t = rem // 10
                u = rem % 10
                if u > 0:
                    words.append(units[u] + " و" + tens[t])
                else:
                    words.append(tens[t])
        return " و".join(words)

    int_part = int(amount)
    dec_part = int(round((amount - int_part) * 100))
    
    mils = int_part // 1000000
    thous = (int_part % 1000000) // 1000
    ones = int_part % 1000
    
    parts = []
    if mils > 0:
        if mils == 1: parts.append("مليون")
        elif mils == 2: parts.append("مليونان")
        else: parts.append(convert_999(mils) + " مليون")
    if thous > 0:
        if thous == 1: parts.append("ألف")
        elif thous == 2: parts.append("ألفان")
        else: parts.append(convert_999(thous) + " ألف")
    if ones > 0:
        parts.append(convert_999(ones))
        
    res = " و".join(parts) + " ريال"
    if dec_part > 0:
        res += " و" + convert_999(dec_part) + " هللة"
    return res + " فقط لا غير"


@app.route("/api/gps_sync", methods=["POST"])
@login_required
def api_gps_sync():
    if "source_file" not in request.files or "target_file" not in request.files:
        return jsonify({"success": False, "error": "الرجاء رفع الملفين المطلوبة"}), 400

    src_file = request.files["source_file"]
    tgt_file = request.files["target_file"]

    try:
        wb_src = openpyxl.load_workbook(src_file, data_only=True)
        ws_src = wb_src.active

        headers = {}
        for c in range(1, ws_src.max_column + 1):
            val = ws_src.cell(row=4, column=c).value
            if val:
                headers[str(val).strip()] = c

        if "رقم اللوحة" not in headers:
            headers = {}
            for c in range(1, ws_src.max_column + 1):
                val = ws_src.cell(row=1, column=c).value
                if val:
                    headers[str(val).strip()] = c

        lookup = {}
        plate_src_col = headers.get("رقم اللوحة")
        if plate_src_col:
            # Data starts after header
            start_row = (
                5
                if "رقم اللوحة"
                in [
                    ws_src.cell(row=4, column=c).value
                    for c in range(1, ws_src.max_column + 1)
                ]
                else 2
            )
            for r in range(start_row, ws_src.max_row + 1):
                plate_val = ws_src.cell(row=r, column=plate_src_col).value
                norm = normalize_plate(plate_val)
                if norm:
                    row_data = {}
                    for col_name, c_idx in headers.items():
                        row_data[col_name] = ws_src.cell(row=r, column=c_idx).value
                    lookup[norm] = row_data

        wb = openpyxl.load_workbook(tgt_file)
        ws = wb.active

        plate_col = 9
        vin_col = 1
        sn_col = 2
        year_col = 3
        model_col = 4
        make_col = 5
        reg_col = 6
        branch_col = 7

        match_count = 0
        update_count = 0

        for r in range(6, ws.max_row + 1):
            plate_val = ws.cell(row=r, column=plate_col).value
            if not plate_val:
                continue
            norm = normalize_plate(plate_val)
            if norm in lookup:
                src = lookup[norm]
                match_count += 1
                updates = [
                    (vin_col, "رقم الهيكل"),
                    (sn_col, "الرقم التسلسلي"),
                    (year_col, "سنة الصنع"),
                    (model_col, "الطراز"),
                    (make_col, "الماركة"),
                    (reg_col, "نوع التسجيل"),
                    (branch_col, "الفرع"),
                ]
                for col_idx, src_col_name in updates:
                    if src_col_name in src:
                        new_val = src[src_col_name]
                        if (
                            new_val is not None
                            and str(new_val).strip() != ""
                            and str(new_val).lower() != "nan"
                        ):
                            ws.cell(row=r, column=col_idx).value = new_val
                            update_count += 1

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode("utf-8")

        return jsonify(
            {
                "success": True,
                "matches": match_count,
                "updates": update_count,
                "file_b64": b64,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/drivers", methods=["POST"])
@login_required
def add_driver():
    data = request.json or {}
    name = data.get("name", "").strip()
    empid = data.get("empid", "").strip()
    plate = data.get("plate", "").strip()
    car = data.get("car", "").strip()
    iqama = data.get("iqama", "").strip()
    phone = data.get("phone", "").strip()
    drivercard = data.get("drivercard", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    if is_workstation():
        # Workstation: persist to the isolated drivers_ws blob (id=2). Real table untouched.
        lst = blob_get("drivers_ws") or []
        new_id = max([d.get("id", 0) for d in lst], default=0) + 1
        row = {"id": new_id, "name": name, "empid": empid, "plate": plate, "car": car,
               "iqama": iqama, "phone": phone, "drivercard": drivercard}
        lst.append(row)
        blob_set("drivers_ws", lst)
        return jsonify({"success": True, **row})
    with db_connection() as conn:
        c = conn.cursor()
        if USE_POSTGRES:
            c.execute(
                "INSERT INTO drivers (name, empid, plate, car, iqama, phone, drivercard) "
                "VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id",
                (name, empid, plate, car, iqama, phone, drivercard),
            )
            new_id = c.fetchone()["id"]
            conn.commit()
        else:
            c.execute(
                "INSERT INTO drivers (name, empid, plate, car, iqama, phone, drivercard) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, empid, plate, car, iqama, phone, drivercard),
            )
            conn.commit()
            new_id = c.lastrowid
    logger.info("Driver added: %s (id=%s)", name, new_id)
    return jsonify(
        {
            "success": True,
            "id": new_id,
            "name": name,
            "plate": plate,
            "car": car,
            "iqama": iqama,
            "phone": phone,
            "drivercard": drivercard,
        }
    )


@app.route("/api/drivers/<int:driver_id>", methods=["DELETE"])
@login_required
def delete_driver(driver_id):
    if is_workstation():
        # Workstation: remove from the isolated drivers_ws blob (id=2). Real table untouched.
        lst = [d for d in (blob_get("drivers_ws") or []) if d.get("id") != driver_id]
        blob_set("drivers_ws", lst)
        return jsonify({"success": True})
    with db_connection() as conn:
        conn.execute("DELETE FROM drivers WHERE id = ?", (driver_id,))
        conn.commit()
    logger.info("Driver deleted: id=%d", driver_id)
    return jsonify({"success": True})


@app.route("/api/drivers/<int:driver_id>", methods=["PUT"])
@login_required
def update_driver(driver_id):
    data = request.json or {}
    name = data.get("name", "").strip()
    empid = data.get("empid", "").strip()
    plate = data.get("plate", "").strip()
    car = data.get("car", "").strip()
    iqama = data.get("iqama", "").strip()
    phone = data.get("phone", "").strip()
    drivercard = data.get("drivercard", "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if is_workstation():
        # Workstation: update inside the isolated drivers_ws blob (id=2). Real table untouched.
        lst = blob_get("drivers_ws") or []
        for d in lst:
            if d.get("id") == driver_id:
                d.update({"name": name, "empid": empid, "plate": plate, "car": car,
                          "iqama": iqama, "phone": phone, "drivercard": drivercard})
                break
        blob_set("drivers_ws", lst)
        return jsonify({"success": True, "id": driver_id, "name": name, "plate": plate, "car": car,
                        "iqama": iqama, "phone": phone, "drivercard": drivercard})

    with db_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            UPDATE drivers
            SET name=?, empid=?, plate=?, car=?, iqama=?, phone=?, drivercard=?
            WHERE id=?
        """,
            (name, empid, plate, car, iqama, phone, drivercard, driver_id),
        )
        conn.commit()

    logger.info("Driver updated: %s (id=%d)", name, driver_id)
    return jsonify(
        {
            "success": True,
            "id": driver_id,
            "name": name,
            "plate": plate,
            "car": car,
            "iqama": iqama,
            "phone": phone,
            "drivercard": drivercard,
        }
    )


@app.route("/api/generate_po", methods=["POST"])
@login_required
def generate_po():
    """Generate PO Excel from original template using openpyxl server-side"""
    try:
        data = request.json or {}

        template_path = os.path.join(os.path.dirname(__file__), "po_template.xlsx")
        if not os.path.exists(template_path):
            logger.error("PO template not found at: %s", template_path)
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "قالب طلب الشراء غير موجود (po_template.xlsx)",
                    }
                ),
                500,
            )

        wb = openpyxl.load_workbook(template_path)
        ws = wb.active

        ws["D7"] = data.get("driver", "")
        ws["G7"] = data.get("branch", "الدمام")
        ws["I7"] = data.get("job", "سائق")
        ws["D8"] = data.get("car", "")
        ws["G8"] = data.get("plate", "")
        
        model_val = data.get("model", "")
        if not model_val and data.get("car"):
            import re
            match = re.search(r'(\d{4}|[٠١٢٣٤٥٦٧٨٩]{4})', data.get("car", ""))
            if match:
                model_val = match.group(1)
        ws["I8"] = model_val
        
        ws["D9"] = data.get("odometer", "")
        
        try:
            ws.unmerge_cells(start_row=9, start_column=5, end_row=9, end_column=9)
        except Exception:
            pass

        ws["F8"] = "رقم اللوحة:"
        ws["H8"] = "الموديل:"

        ws["F9"] = "رقم الجوال:"
        ws["G9"] = data.get("phone", "")
        ws["H9"] = "الرقم الوظيفي:"
        ws["I9"] = data.get("empid", "")
        
        from openpyxl.styles import PatternFill, Font, Border, Side, Alignment
        label_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")  # neutral gray, B&W-print-safe
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        # Labels to format: F8(Plate), H8(Model), F9(Phone), H9(EmpID)
        for r, c in [(8, 6), (8, 8), (9, 6), (9, 8)]:
            cell = ws.cell(row=r, column=c)
            # Copy font from A8, but hardcode the rest to ensure it matches perfectly
            try:
                cell.font = copy(ws["A8"].font)
            except:
                cell.font = Font(name="Arial", size=12, bold=True)
            cell.fill = label_fill
            cell.border = thin_border
            cell.alignment = center_align
            
        # Values to format: G8(PlateVal), I8(ModelVal), G9(PhoneVal), I9(EmpIDVal)
        for r, c in [(8, 7), (8, 9), (9, 7), (9, 9)]:
            cell = ws.cell(row=r, column=c)
            try:
                cell.font = copy(ws["D8"].font)
            except:
                pass
            cell.border = thin_border
            cell.alignment = center_align

        date_val = data.get("date", "")
        if date_val:
            ws["C4"] = date_val
        serial_val = data.get("serial", "")
        if serial_val:
            ws["J3"] = f"NO. {serial_val}"

        from openpyxl.styles import Alignment
        center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)

        def set_formatted(row, col, val, is_currency=False):
            cell = ws.cell(row=row, column=col)
            if not isinstance(cell, MC):
                if val is not None and val != "":
                    if is_currency:
                        try:
                            cell.value = float(val)
                            cell.number_format = '#,##0.00'
                        except:
                            cell.value = val
                    else:
                        cell.value = val
                else:
                    cell.value = None
                cell.alignment = center_align

        # Fill parts (rows 12-14)
        parts = data.get("parts", [])
        for i, p in enumerate(parts[:3]):
            r = 12 + i
            set_formatted(r, 4, p.get("desc", ""))
            set_formatted(r, 7, p.get("qty"))
            set_formatted(r, 8, p.get("price"), is_currency=True)
            set_formatted(r, 9, p.get("val"), is_currency=True)
            set_formatted(r, 10, p.get("notes", ""))

        # Fill repairs (rows 18-20)
        repairs = data.get("repairs", [])
        for i, rep in enumerate(repairs[:3]):
            r = 18 + i
            set_formatted(r, 4, rep.get("desc", ""))
            set_formatted(r, 8, rep.get("val"), is_currency=True)
            set_formatted(r, 9, rep.get("notes", ""))

        # Fill tires (rows 24-26)
        tires = data.get("tires", [])
        for i, t in enumerate(tires[:3]):
            r = 24 + i
            set_formatted(r, 4, t.get("date", ""))
            set_formatted(r, 5, t.get("count"))
            set_formatted(r, 6, t.get("front"))
            set_formatted(r, 7, t.get("back"))
            set_formatted(r, 8, t.get("prev"))
            set_formatted(r, 9, t.get("curr"))
            set_formatted(r, 10, t.get("dist"))

        # Fill batteries (rows 30-32)
        batteries = data.get("batteries", [])
        for i, b in enumerate(batteries[:3]):
            r = 30 + i
            set_formatted(r, 4, b.get("desc", ""))
            set_formatted(r, 6, b.get("count"))
            set_formatted(r, 7, b.get("size", ""))
            set_formatted(r, 8, b.get("amp", ""))
            set_formatted(r, 9, b.get("price"), is_currency=True)
            set_formatted(r, 10, b.get("date", ""))

        # Fill summary totals (row 34: per-category, row 35-36: subtotals, row 37: grand total)
        summary = data.get("summary", {})

        # Row 34: individual category totals
        set_formatted(35, 3, summary.get("parts_total"), is_currency=True)
        set_formatted(35, 4, summary.get("repairs_total"), is_currency=True)
        set_formatted(35, 5, summary.get("tires_total"), is_currency=True)
        set_formatted(35, 6, summary.get("batteries_total"), is_currency=True)
        # Row 34 col 7-8: "الإجمالي شامل الضريبة" (label already in template)
        set_formatted(35, 7, summary.get("grand_total"), is_currency=True)
        # Row 34 col 9: Notes
        notes = data.get("notes", "")
        if notes:
            set_formatted(35, 9, notes)

        # Row 37: الإجمالي شامل الضريبة (grand total line) - Replaced with Tafqeet text
        grand_total_val = summary.get("grand_total")
        
        # Add Tafqeet in Col 5 (E) of Row 37 INSTEAD of the numeric value
        ws.cell(row=37, column=5).value = tafqeet(grand_total_val)
        ws.cell(row=37, column=5).alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

        # Remove the previous logic that put it in Col 1
        ws.cell(row=37, column=1).value = ""

        # Inject Logo
        try:
            from openpyxl.drawing.image import Image as XLImage
            logo_path = os.path.join(os.path.dirname(__file__), "logo_excel.png")
            if not os.path.exists(logo_path):
                logo_path = os.path.join(os.path.dirname(__file__), "static", "site_logo.png")
            if os.path.exists(logo_path):
                img = XLImage(logo_path)
                img.width = 450
                img.height = 85
                ws.add_image(img, 'C1') 
        except Exception as e:
            logger.error("Logo injection failed: %s", e)

        # Clean black-&-white printing: fit to one page width, centered, A4 portrait.
        try:
            from openpyxl.worksheet.properties import PageSetupProperties
            from openpyxl.worksheet.page import PageMargins
            ws.page_setup.orientation = "portrait"
            ws.page_setup.fitToWidth = 1
            ws.page_setup.fitToHeight = 0
            ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
            ws.print_options.horizontalCentered = True
            ws.page_margins = PageMargins(left=0.3, right=0.3, top=0.5, bottom=0.5, header=0.2, footer=0.2)
        except Exception as e:
            logger.warning("PO page setup skipped: %s", e)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        b64 = base64.b64encode(output.read()).decode("utf-8")
        return jsonify({"success": True, "file_b64": b64})
    except Exception as e:
        logger.exception("generate_po error")
        return jsonify({"success": False, "error": "تعذّر توليد طلب الشراء."}), 500


@app.route("/api/generate_oils", methods=["POST"])
@login_required
def generate_oils():
    """Generate Oils/Filters Excel from original template using openpyxl server-side"""
    try:
        data = request.json or {}

        template_path = os.path.join(os.path.dirname(__file__), "oils_template.xlsx")
        if not os.path.exists(template_path):
            logger.error("Oils template not found at: %s", template_path)
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "قالب الزيوت غير موجود (oils_template.xlsx)",
                    }
                ),
                500,
            )

        wb = openpyxl.load_workbook(template_path)
        ws = wb.active

        def safe_set(row, col, val):
            cell = ws.cell(row=row, column=col)
            if not isinstance(cell, MC):
                cell.value = val

        # Update title (row 4)
        title = data.get("title", "")
        if title:
            ws["A4"] = title

        # Fill main oil data (rows 6-62, max 57 rows)
        oils = data.get("oils", [])
        for i, oil in enumerate(oils[:57]):
            r = 6 + i
            safe_set(r, 1, i + 1)  # م
            safe_set(r, 2, oil.get("plate", ""))  # رقم لوحة
            safe_set(r, 3, oil.get("driver", ""))  # المستخدم (merged C:D)
            safe_set(r, 5, oil.get("date", ""))  # تاريخ تغيير الزيت
            safe_set(r, 6, oil.get("counter", ""))  # رقم العداد
            safe_set(r, 7, oil.get("liters", ""))  # عدد اللترات
            safe_set(r, 8, oil.get("filters", ""))  # عدد الفلاتر

        # Fill filter details - LEFT side (A-E, rows 69-86)
        filters_left = data.get("filters_left", [])
        for i, f in enumerate(filters_left[:18]):
            r = 69 + i
            safe_set(r, 1, i + 1)
            safe_set(r, 2, f.get("name", ""))
            safe_set(r, 3, f.get("prev", ""))
            safe_set(r, 4, f.get("used", ""))
            safe_set(r, 5, f.get("remaining", ""))

        # Fill filter details - RIGHT side (F-H, rows 69-86)
        filters_right = data.get("filters_right", [])
        for i, f in enumerate(filters_right[:18]):
            r = 69 + i
            safe_set(r, 6, len(filters_left) + i + 1)
            safe_set(r, 7, f.get("name", ""))
            safe_set(r, 8, f.get("qty", ""))

        # Fill notes section (rows 65-66 only; 63 and 67 are fixed headers in template)
        notes = data.get("notes", {})
        if notes.get("row65"):
            safe_set(65, 1, notes["row65"])
        if notes.get("row66"):
            safe_set(66, 1, notes["row66"])

        # Fill diesel filter notes (rows 88-95)
        diesel_notes = data.get("diesel_notes", [])
        for i, note in enumerate(diesel_notes[:8]):
            safe_set(88 + i, 1, note)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        b64 = base64.b64encode(output.read()).decode("utf-8")
        return jsonify({"success": True, "file_b64": b64})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/send_email", methods=["POST"])
@login_required
def send_email():
    data = request.json or {}
    recipient = (data.get("email") or "").strip()
    filename = data.get("filename", "invoice.xlsx")
    file_b64 = data.get("file_b64", "")
    custom_subject = data.get("subject", "").strip()
    cc_list = data.get("cc", [])

    # Validate required fields
    if not recipient:
        return jsonify({"error": "البريد الإلكتروني مطلوب"}), 400
    if not file_b64:
        return jsonify({"error": "بيانات الملف مطلوبة"}), 400
    # Basic email format check
    if "@" not in recipient or "." not in recipient.split("@")[-1]:
        return jsonify({"error": f"عنوان البريد غير صالح: {recipient}"}), 400

    try:
        file_data = base64.b64decode(file_b64)
        sender_email = app.config["MAIL_USERNAME"]

        # Dynamic subject
        if custom_subject:
            subject = custom_subject
        elif "زيوت" in filename or "فلاتر" in filename:
            subject = "بيان استهلاك الزيوت والفلاتر"
        elif "شراء" in filename or "طلب" in filename:
            subject = "طلب شراء وإصلاح"
        else:
            subject = "فاتورة صيانة"

        all_recipients = [recipient]
        cc_emails = [e.strip() for e in cc_list if e.strip()]

        msg = Message(
            subject,
            sender=sender_email,
            recipients=all_recipients,
            cc=cc_emails if cc_emails else [],
        )

        msg.body = _build_plain_text(subject, filename)
        msg.html = _build_html_email(subject, filename)
        msg.attach(
            filename,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            file_data,
        )

        mail.send(msg)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/compose_email", methods=["POST"])
@login_required
def compose_email():
    recipient = request.form.get("email")
    subject = request.form.get("subject", "BIN ZOMAH INTL.")
    body_text = request.form.get("body", "")
    file = request.files.get("attachment")
    cc_list = request.form.getlist("cc")

    if not recipient:
        return jsonify({"error": "Missing email"}), 400

    try:
        cc_emails = [e.strip() for e in cc_list if e.strip()]
        msg = Message(
            subject,
            sender=app.config["MAIL_USERNAME"],
            recipients=[recipient],
            cc=cc_emails if cc_emails else [],
        )

        msg.body = f"{body_text}\n\n{'—' * 40}\nKHALED AL-GHAMDI\nFleet Management Department\nBIN ZOMAH INTL. Trading & Development Co., Ltd.\nM: +966 53 975 7659\nE: damfleet@bz.sa"
        msg.html = _build_html_compose(subject, body_text)

        if file and file.filename:
            msg.attach(
                file.filename,
                file.content_type or "application/octet-stream",
                file.read(),
            )

        mail.send(msg)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _build_plain_text(subject, filename):
    return (
        f"{subject}\n"
        f"{'—' * 40}\n\n"
        f"Attached: {filename}\n\n"
        f"{'—' * 40}\n"
        f"KHALED AL-GHAMDI\n"
        f"Fleet Management Department\n"
        f"BIN ZOMAH INTL. Trading & Development Co., Ltd.\n"
        f"M: +966 53 975 7659\n"
        f"E: damfleet@bz.sa\n"
        f"{'—' * 40}\n"
        f"This email is auto-generated. Please do not reply directly."
    )


def _build_html_email(subject, filename):
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f4f4f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f7;padding:30px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06);">

<!-- Header -->
<tr><td style="background:#0C2340;padding:20px 40px;">
<table width="100%" cellpadding="0" cellspacing="0"><tr>
<td style="text-align:right;vertical-align:middle;">
<h1 style="margin:0;color:#ffffff;font-size:20px;font-weight:700;letter-spacing:1px;">BIN ZOMAH INTL.</h1>
<p style="margin:4px 0 0;color:rgba(255,255,255,0.6);font-size:11px;letter-spacing:2px;text-transform:uppercase;">Trading & Development Co., Ltd.</p>
</td>
</tr></table>
</td></tr>

<!-- Subject Bar -->
<tr><td style="background:#f8f9fa;padding:16px 40px;border-bottom:1px solid #e9ecef;">
<p style="margin:0;color:#0C2340;font-size:15px;font-weight:600;">{subject}</p>
</td></tr>

<!-- Body -->
<tr><td style="padding:32px 40px;">
<p style="margin:0 0 20px;color:#333;font-size:15px;line-height:1.7;">
يرجى الاطلاع على الملف المرفق أدناه.
</p>

<!-- Attachment Card -->
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f9fa;border:1px solid #e9ecef;border-radius:8px;margin:0 0 24px;">
<tr>
<td style="padding:14px 18px;width:40px;vertical-align:middle;">
<div style="width:36px;height:36px;background:#0C2340;border-radius:8px;text-align:center;line-height:36px;font-size:16px;color:#fff;">📎</div>
</td>
<td style="padding:14px 18px 14px 0;">
<p style="margin:0;font-size:14px;font-weight:600;color:#333;">{filename}</p>
<p style="margin:2px 0 0;font-size:12px;color:#888;">Excel Document (.xlsx)</p>
</td>
</tr>
</table>
</td></tr>

<!-- Divider -->
<tr><td style="padding:0 40px;"><div style="border-top:1px solid #e9ecef;"></div></td></tr>

<!-- Signature -->
<tr><td style="padding:24px 40px 20px;">
<table cellpadding="0" cellspacing="0">
<tr>
<td style="padding-left:16px;border-left:3px solid #0C2340;">
<p style="margin:0;font-size:14px;font-weight:700;color:#0C2340;">KHALED AL-GHAMDI</p>
<p style="margin:3px 0 0;font-size:12px;color:#666;">خالد بن محمد الغامدي</p>
<p style="margin:8px 0 0;font-size:12px;color:#888;line-height:1.6;">
Fleet Management Department<br>
BIN ZOMAH INTL. Trading & Development Co., Ltd.
</p>
<p style="margin:8px 0 0;font-size:12px;color:#888;">
M: +966 53 975 7659 &nbsp;|&nbsp; E: damfleet@bz.sa
</p>
</td>
</tr>
</table>
</td></tr>

<!-- Footer -->
<tr><td style="background:#f8f9fa;padding:16px 40px;border-top:1px solid #e9ecef;text-align:center;">
<p style="margin:0;font-size:11px;color:#aaa;line-height:1.5;">
هذا البريد الإلكتروني تم إرساله تلقائياً — يرجى عدم الرد مباشرة على هذه الرسالة.
<br>This is an automated message. Please do not reply directly.
</p>
</td></tr>

</table>
</td></tr></table>
</body></html>"""


def _build_html_compose(subject, body_text):
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f4f4f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f7;padding:30px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06);">

<!-- Header -->
<tr><td style="background:#0C2340;padding:20px 40px;">
<table width="100%" cellpadding="0" cellspacing="0"><tr>
<td style="text-align:right;vertical-align:middle;">
<h1 style="margin:0;color:#ffffff;font-size:20px;font-weight:700;letter-spacing:1px;">BIN ZOMAH INTL.</h1>
<p style="margin:4px 0 0;color:rgba(255,255,255,0.6);font-size:11px;letter-spacing:2px;text-transform:uppercase;">Trading & Development Co., Ltd.</p>
</td>
</tr></table>
</td></tr>

<!-- Body -->
<tr><td style="padding:32px 40px;">
<div style="color:#333;font-size:15px;line-height:1.8;white-space:pre-line;">{body_text}</div>
</td></tr>

<!-- Divider -->
<tr><td style="padding:0 40px;"><div style="border-top:1px solid #e9ecef;"></div></td></tr>

<!-- Signature -->
<tr><td style="padding:24px 40px 20px;">
<table cellpadding="0" cellspacing="0">
<tr>
<td style="padding-left:16px;border-left:3px solid #0C2340;">
<p style="margin:0;font-size:14px;font-weight:700;color:#0C2340;">KHALED AL-GHAMDI</p>
<p style="margin:3px 0 0;font-size:12px;color:#666;">خالد بن محمد الغامدي</p>
<p style="margin:8px 0 0;font-size:12px;color:#888;line-height:1.6;">
Fleet Management Department<br>
BIN ZOMAH INTL. Trading & Development Co., Ltd.
</p>
<p style="margin:8px 0 0;font-size:12px;color:#888;">
M: +966 53 975 7659 &nbsp;|&nbsp; E: damfleet@bz.sa
</p>
</td>
</tr>
</table>
</td></tr>

<!-- Footer -->
<tr><td style="background:#f8f9fa;padding:16px 40px;border-top:1px solid #e9ecef;text-align:center;">
<p style="margin:0;font-size:11px;color:#aaa;">
This message was sent from BIN ZOMAH INTL. Fleet Management System.
</p>
</td></tr>

</table>
</td></tr></table>
</body></html>"""


# Mirror every /api/* endpoint under /importantworkstation/api/* (same handler). Because
# is_workstation() is path-based, those calls transparently read/write the id=2 sandbox,
# while the real /api/* endpoints (id=1) stay completely untouched.
for _rule in list(app.url_map.iter_rules()):
    if _rule.rule.startswith("/api/"):
        app.add_url_rule(
            WS_PREFIX + _rule.rule,
            endpoint="ws_" + _rule.endpoint,
            view_func=app.view_functions[_rule.endpoint],
            methods=sorted(_rule.methods - {"HEAD", "OPTIONS"}),
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    logger.info("Starting server on port %d (debug=%s)", port, debug)
    app.run(host="0.0.0.0", port=port, debug=debug)

