import os
import io
import logging
import shutil
import openpyxl
from contextlib import contextmanager
from openpyxl.drawing.image import Image as XLImage
from openpyxl.cell.cell import MergedCell as MC
import sqlite3
import base64
import requests
import json
import re
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
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

DB_PATH = os.path.join(os.path.dirname(__file__), "database.sqlite")
# Fallback for Linux hosting environments (Render, Arabcord, etc.)
if os.name == "posix":
    DB_PATH = "/tmp/database.sqlite"

LOGO_PATH = os.path.join(os.path.dirname(__file__), "static", "excel_logo.png")

# Valid tab names for template upload
VALID_TABS = {"invoice", "oils", "purchase", "schedule"}
# Default template filenames (fallback)
DEFAULT_TEMPLATES = {
    "oils": "oils_template.xlsx",
    "purchase": "po_template.xlsx",
    "schedule": "schedule_base.xlsx",
}

# Logo for email headers (120x80px PNG, white bg)
EMAIL_LOGO_B64 = "iVBORw0KGgoAAAANSUhEUgAAAHgAAABQCAIAAABd+SbeAAAGl0lEQVR42u3abWybVxUH8HPu47eSxHFiu3GTKW5e3KR5aZhDOkqmFhoxadpg0wqCIugEqwZsIAqIicKmdqNiCLURQhvdBmXVVrUrRJ3WoWpsq1iaboNuTZs0IU7avGyu06RJ7Dh+t597Dx9cYOpgdBMTj9H5f/AXPx8e/XR17z3nPEhEwPnwI5iAoRmaw9AMzdAchmZoDkMzNENzGJqhOQzN0AzNYWiG5jA0QzM0h6HfHQIoxMG9KDhlBEAsPOtCgiYCBFBSZbKy4KxFgRBfSSSWvXv30Bd2nLkcTuetlSKG/q8FERFRCBydSvyud/6lM9ETZ+elVAgkBKpCWNto5E/CpCQCQIS3Q3PBS5elpMrlJSeH0WTCdp996+4Rq0176M7aDX6XLsmkIUN/0B0ZAQAy6fjQ6CQRIUJOV6V2ezyRtpcsOztp3dodKCvW9t/XtPFjbqlIE8jQ748YABDh0Iuh8JIOoABRE6jrZC/Suq63DQTGE8ncuraVpyfMW7sDVjM++YOmT691KyKByNDXfE1WJAQ++OT53b+/mEgrRKT8HwCU1e+8ecXOLZ/j8RCqd+3ibdzSobXtsXCD17GjtaCqjIhKGXNcmoykDgRC4c9/57mdDFQ7L5o3L7RbUpcqfiELgXCQdnBfr/I19b4y8PjD1qY762ztde/8wPTQZX9tcpkuGvrZrHADs2j/e/WzIvkzs+UbdWp89GVpwOoob6uuuerhrnfNLfYOXw3GzSWgCgWQmk7JalxtzZLB6BGOJ3OHeuZsJn97W2FKdOX5qvNJdmiXHZ3/Yn0rpRCQQzSbNSfedz9RvWrg5HokpmgEApGApc8HiqqirK/3GQMvS/hhYCECGdzj3+3cZWb6avf8LjdGy4oXlkKnv8bPTSg5PxZzKS9p1LHZX/YeKDnw4xeVIkRFSORKZ2EkT8Kkz0N/ZGbB41DY3VNyc3+8upC7MlMRKZKV6EjOE2vk6xK2z7yeEMPlugbpoCdAzDdqdKnvnd49AQBgt9u1Df2Ct1gsqizLeNovNhp0+C2OA8koaQnp9/rO2/aKxSaD7qM0c2S9LTfqSPVL+g7gdLk3R4Lvn7+mOzy/opoQygzl5NQIq0/p5lhK0e2LzTzqGkWc+MfHZXRCoZDRfINvaOwiz6hElTDSJI1SP3BSkjGC9pRbIp/87qt+t6PBqkEYVgcUzn9CAABxl/mB7nH0vYi07reLMYozcWJtqzI2u8KnIVC0eTcdVgg//uLewJtFRfvcQCkKR1Bh/zeUZYrtdqSVVnXmdI4JjvQEzWUyIPV+s7p1f5Zk8HkDQ5a8h0/4lTsdTtiCWifdzGoFQylFZ2t+TNl1tN2TVdJW99ddpChfbuVZGXiXku/4WVeK/MlA9GqOFK+HGgnWaVXKgvnXjSkLjWEYhmEYhmEYhmEYhmH+sz8BzQDdMcl1yrQAAAAASUVORK5CYII="

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
_secret = os.environ.get("SECRET_KEY")
if not _secret:
    logger.warning(
        "SECRET_KEY not set — using insecure default. Set it in .env for production!"
    )
    _secret = "super_secret_session_key_12345"
app.secret_key = _secret
CORS(app)

# Session lifetime: 8 hours
from datetime import timedelta

app.permanent_session_lifetime = timedelta(hours=8)

# ── GPS Configuration ────────────────────────────────────────────────────────
GPS_USER = os.environ.get("GPS_USER", "")
GPS_PASS = os.environ.get("GPS_PASS", "")
GPS_ASSET_URL = os.environ.get(
    "GPS_ASSET_URL", "https://fleetmanagement-clust03.gpscockpit.com/#/FleetOverview"
)
GPS_PERMANENT_TOKEN = os.environ.get("GPS_PERMANENT_TOKEN", "")


def get_gps_token():
    """Return the permanent GPS API token from environment."""
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
def get_gps_locations():
    token = get_gps_token()
    if not token:
        return (
            jsonify(
                {
                    "error": "فشل في الحصول على مفتاح الوصول — GPS_PERMANENT_TOKEN غير محدد"
                }
            ),
            401,
        )

    headers = {
        "Authorization": f"GpsCockpitApiKey {token}",
        "Accept": "application/json",
    }
    try:
        response = requests.get(GPS_ASSET_URL, headers=headers, timeout=20)
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify(
                {
                    "error": "GPS API Error",
                    "status_code": response.status_code,
                    "response": response.text[:200],
                }
            ),
            response.status_code,
        )
    except requests.Timeout:
        return jsonify({"error": "GPS API timeout — تجاوز وقت الاستجابة"}), 504
    except requests.ConnectionError:
        return jsonify({"error": "GPS API unreachable — تعذر الاتصال"}), 503
    except Exception as e:
        logger.error("GPS API error: %s", e)
        return jsonify({"error": str(e)}), 500


# Flask-Mail Configuration
app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "True").lower() == "true"
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
mail = Mail(app)

# OAuth Configuration
oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def get_db():
    """Open a database connection with Row factory."""
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


def init_db():
    """Initialize database tables if they don't exist."""
    with app.app_context():
        with db_connection() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS drivers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    empid TEXT,
                    plate TEXT,
                    car TEXT,
                    iqama TEXT,
                    phone TEXT
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS washing_schedule (
                    id INTEGER PRIMARY KEY,
                    data TEXT NOT NULL
                )
            """)
            
            # Auto-seed database from drivers_data.js if missing new drivers
            count = db.execute("SELECT COUNT(*) FROM drivers").fetchone()[0]
            if count < 70:
                js_path = os.path.join(app.root_path, "drivers_data.js")
                if os.path.exists(js_path):
                    try:
                        import json
                        with open(js_path, "r", encoding="utf-8") as f:
                            content = f.read().replace("const driversData = ", "").strip()
                            if content.endswith(";"): content = content[:-1]
                            data = json.loads(content)
                            db.execute("DELETE FROM drivers") # Clear old incomplete data
                            for d in data:
                                db.execute("INSERT INTO drivers (name, empid, plate, car, iqama, phone) VALUES (?, ?, ?, ?, ?, ?)",
                                           (d.get("name", ""), d.get("empid", ""), d.get("plate", ""), d.get("car", ""), d.get("iqama", ""), d.get("phone", "")))
                        logger.info("Database re-seeded with %d drivers from drivers_data.js", len(data))
                    except Exception as e:
                        logger.error("Error seeding DB: %s", e)
            
            db.commit()
    logger.info("Database initialized successfully.")

init_db()


# Security Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("password_entry"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/login")
def login():
    if session.get("authenticated"):
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/google-login")
def google_login():
    redirect_uri = url_for("authorize", _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route("/authorize")
def authorize():
    token = google.authorize_access_token()
    user = google.parse_id_token(token, nonce=None)
    if user:
        session["google_user"] = user
        return redirect(url_for("password_entry"))
    return redirect(url_for("login"))


@app.route("/password", methods=["GET", "POST"])
def password_entry():
    if request.method == "POST":
        pw = request.form.get("password", "")
        master = os.environ.get("MASTER_PASSWORD")
        if not master:
            logger.error("MASTER_PASSWORD environment variable is not set!")
            return render_template(
                "password.html", error="خطأ في إعداد النظام. يرجى التواصل مع المدير."
            )
        if pw == master:
            session["authenticated"] = True
            session.permanent = True
            logger.info("Successful password login")
            return redirect(url_for("index"))
        else:
            logger.warning("Failed login attempt")
            return render_template("password.html", error="كلمة المرور غير صحيحة")
    return render_template("password.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


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


@app.route("/gps_sync")
@login_required
def gps_sync():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("gps_sync.html", google_user=google_user, b64_en=b64_en)


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
            # Scale down to fit nicely in Excel header (Original 1602x481)
            img.width = 300
            img.height = 90
            # Put logo around center (column E/F, top)
            ws.add_image(img, "F1")

        for idx, v in enumerate(vehicles):
            r = 5 + idx
            ws.cell(row=r, column=1, value=v.get("id", idx + 1))
            ws.cell(row=r, column=2, value=v.get("plate", ""))
            ws.cell(row=r, column=3, value=v.get("type", ""))
            ws.cell(row=r, column=4, value=v.get("driver", ""))
            months = v.get("m", [])
            total = sum(months)
            for m_idx in range(12):
                val = "استلم" if months[m_idx] == 1 else None
                ws.cell(row=r, column=5 + m_idx, value=val)
            ws.cell(row=r, column=17, value=total)

        # Add summary stats (similar to what was in row 2 of template)
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
    if request.method == "POST":
        try:
            data_str = json.dumps(request.json.get("vehicles", []))
            with db_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT id FROM washing_schedule WHERE id = 1")
                if c.fetchone():
                    c.execute(
                        "UPDATE washing_schedule SET data = ? WHERE id = 1", (data_str,)
                    )
                else:
                    c.execute(
                        "INSERT INTO washing_schedule (id, data) VALUES (1, ?)",
                        (data_str,),
                    )
                conn.commit()
            return jsonify({"success": True})
        except Exception as e:
            logger.error("washing_data POST error: %s", e)
            return jsonify({"success": False, "error": str(e)}), 500
    else:
        try:
            with db_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT data FROM washing_schedule WHERE id = 1")
                row = c.fetchone()
            if row:
                return jsonify({"success": True, "vehicles": json.loads(row["data"])})
            return jsonify({"success": False, "vehicles": []})
        except Exception as e:
            logger.error("washing_data GET error: %s", e)
            return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/drivers", methods=["GET"])
@login_required
def get_drivers():
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
    if not name:
        return jsonify({"error": "Name is required"}), 400
    with db_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO drivers (name, empid, plate, car, iqama, phone) VALUES (?, ?, ?, ?, ?, ?)",
            (name, empid, plate, car, iqama, phone),
        )
        conn.commit()
        new_id = c.lastrowid
    logger.info("Driver added: %s (id=%d)", name, new_id)
    return jsonify(
        {
            "success": True,
            "id": new_id,
            "name": name,
            "plate": plate,
            "car": car,
            "iqama": iqama,
            "phone": phone,
        }
    )


@app.route("/api/drivers/<int:driver_id>", methods=["DELETE"])
@login_required
def delete_driver(driver_id):
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

    if not name:
        return jsonify({"error": "Name is required"}), 400

    with db_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            UPDATE drivers 
            SET name=?, empid=?, plate=?, car=?, iqama=?, phone=?
            WHERE id=?
        """,
            (name, empid, plate, car, iqama, phone, driver_id),
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
        ws["I8"] = data.get("model", "")
        date_val = data.get("date", "")
        if date_val:
            ws["C4"] = date_val
        serial_val = data.get("serial", "")
        if serial_val:
            ws["J3"] = f"NO. {serial_val}"

        # Fill parts (rows 12-14)
        parts = data.get("parts", [])
        for i, p in enumerate(parts[:3]):
            r = 12 + i
            ws.cell(row=r, column=4).value = p.get("desc", "")
            ws.cell(row=r, column=7).value = p.get("qty") or None
            ws.cell(row=r, column=8).value = p.get("price") or None
            ws.cell(row=r, column=9).value = p.get("val") or None
            ws.cell(row=r, column=10).value = p.get("notes", "")

        # Fill repairs (rows 18-20)
        repairs = data.get("repairs", [])
        for i, rep in enumerate(repairs[:3]):
            r = 18 + i
            ws.cell(row=r, column=4).value = rep.get("desc", "")
            ws.cell(row=r, column=8).value = rep.get("val") or None
            ws.cell(row=r, column=9).value = rep.get("notes", "")

        # Fill tires (rows 24-26)
        tires = data.get("tires", [])
        for i, t in enumerate(tires[:3]):
            r = 24 + i
            ws.cell(row=r, column=4).value = t.get("date", "")
            ws.cell(row=r, column=5).value = t.get("count") or None
            ws.cell(row=r, column=6).value = t.get("front") or None
            ws.cell(row=r, column=7).value = t.get("back") or None
            ws.cell(row=r, column=8).value = t.get("prev") or None
            ws.cell(row=r, column=9).value = t.get("curr") or None
            ws.cell(row=r, column=10).value = t.get("dist") or None

        # Fill batteries (rows 30-32)
        batteries = data.get("batteries", [])
        for i, b in enumerate(batteries[:3]):
            r = 30 + i
            ws.cell(row=r, column=4).value = b.get("desc", "")
            ws.cell(row=r, column=6).value = b.get("count") or None
            ws.cell(row=r, column=7).value = b.get("size", "")
            ws.cell(row=r, column=8).value = b.get("amp", "")
            ws.cell(row=r, column=9).value = b.get("price") or None
            ws.cell(row=r, column=10).value = b.get("date", "")

        # Fill summary totals (row 34: per-category, row 35-36: subtotals, row 37: grand total)
        summary = data.get("summary", {})

        def po_safe_set(row, col, val):
            cell = ws.cell(row=row, column=col)
            if not isinstance(cell, MC):
                cell.value = val

        # Row 34: individual category totals
        po_safe_set(35, 3, summary.get("parts_total") or None)
        po_safe_set(35, 4, summary.get("repairs_total") or None)
        po_safe_set(35, 5, summary.get("tires_total") or None)
        po_safe_set(35, 6, summary.get("batteries_total") or None)
        # Row 34 col 7-8: "الإجمالي شامل الضريبة" (label already in template)
        po_safe_set(35, 7, summary.get("grand_total") or None)
        # Row 34 col 9: Notes
        notes = data.get("notes", "")
        if notes:
            po_safe_set(35, 9, notes)

        # Row 37: الإجمالي شامل الضريبة (grand total line)
        po_safe_set(37, 5, summary.get("grand_total") or None)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        b64 = base64.b64encode(output.read()).decode("utf-8")
        return jsonify({"success": True, "file_b64": b64})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


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
<p style="margin:3px 0 0;font-size:12px;color:#666;">خالد الغامدي</p>
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
<p style="margin:3px 0 0;font-size:12px;color:#666;">خالد الغامدي</p>
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    logger.info("Starting server on port %d (debug=%s)", port, debug)
    app.run(host="0.0.0.0", port=port, debug=debug)
