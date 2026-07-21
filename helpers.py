"""
helpers.py — Shared utility functions used across all Blueprints.

Extracted from the monolithic app.py to enable modular route organization.
All functions here are imported by route Blueprints as needed.
"""
import os
import re
import json
import html
import secrets
import logging
from datetime import datetime
from functools import wraps

from flask import session, request, redirect, url_for, jsonify, current_app

logger = logging.getLogger('InvoiceApp')

# ── Constants ─────────────────────────────────────────────────────────────────
WS_PREFIX = "/importantworkstation"
AUDIT_MAX = 1000
AUDIT_COALESCE_SEC = 600

BRANCHES = [
    {"id": 1, "name": "الدمام"},
    {"id": 3, "name": "جدة"},
    {"id": 4, "name": "الرياض"},
    {"id": 5, "name": "حفر الباطن"},
    {"id": 6, "name": "بالجرشي"},
    {"id": 7, "name": "جيزان"},
]
BRANCH_IDS = {b["id"] for b in BRANCHES}
BRANCH_NAME = {b["id"]: b["name"] for b in BRANCHES}

SNAP_TAB_BY_ROUTE = {
    "/schedule": "schedule_data", "/washing": "washing_schedule", "/employees": "employees",
    "/records": "records_data", "/incidents": "incidents_data", "/oils": "oils_data",
    "/purchase": "purchase_data", "/workshop": "workshop_data", "/gps_devices": "gps_devices_data",
    "/fuel": "fuel_data",
}

SNAPSHOT_TABLES = {
    "schedule_data", "washing_schedule", "records_data", "employees",
    "incidents_data", "gps_devices_data", "oils_data", "purchase_data", "workshop_data",
    "fuel_data",
}
SNAP_KEEP = 30
SNAP_LABELS = {
    "schedule_data": "الجدول الأسبوعي", "washing_schedule": "الغسيل", "records_data": "التوثيق",
    "employees": "الموظفون", "incidents_data": "الحوادث والمخالفات", "gps_devices_data": "أجهزة التتبع",
    "oils_data": "الزيوت والفلاتر", "purchase_data": "طلبات الشراء", "workshop_data": "الورشة",
    "fuel_data": "تموين المحروقات",
}

# Valid tab names for template upload
VALID_TABS = {"invoice", "oils", "purchase", "schedule", "workshop"}
DEFAULT_TEMPLATES = {
    "oils": "oils_template.xlsx",
    "purchase": "po_template.xlsx",
    "schedule": "schedule_base.xlsx",
    "workshop": "تقرير الورشة.xlsx",
}

# System feature defaults
_DEFAULT_FEATURES = {
    "audit_enforced": True,
    "ai_assistant": True,
    "email_alerts": True,
    "workstation_mode": False,
}

# Logo for email headers
EMAIL_LOGO_B64 = "iVBORw0KGgoAAAANSUhEUgAAAHgAAABQCAIAAABd+SbeAAAGl0lEQVR42u3abWybVxUH8HPu47eSxHFiu3GTKW5e3KR5aZhDOkqmFhoxadpg0wqCIugEqwZsIAqIicKmdqNiCLURQhvdBmXVVrUrRJ3WoWpsq1iaboNuTZs0IU7avGyu06RJ7Dh+t597Dx9cYOpgdBMTj9H5f/AXPx8e/XR17z3nPEhEwPnwI5iAoRmaw9AMzdAchmZoDkMzNENzGJqhOQzN0AzNYWiG5jA0QzM0h6HfHQIoxMG9KDhlBEAsPOtCgiYCBFBSZbKy4KxFgRBfSSSWvXv30Bd2nLkcTuetlSKG/q8FERFRCBydSvyud/6lM9ETZ+elVAgkBKpCWNto5E/CpCQCQIS3Q3PBS5elpMrlJSeH0WTCdp996+4Rq0176M7aDX6XLsmkIUN/0B0ZAQAy6fjQ6CQRIUJOV6V2ezyRtpcsOztp3dodKCvW9t/XtPFjbqlIE8jQ748YABDh0Iuh8JIOoABRE6jrZC/Suq63DQTGE8ncuraVpyfMW7sDVjM++YOmT691KyKByNDXfE1WJAQ++OT53b+/mEgrRKT8HwCU1e+8ecXOLZ/j8RCqd+3ibdzSobXtsXCD17GjtaCqjIhKGXNcmoykDgRC4c9/57mdDFQ7L5o3L7RbUpcqfiELgXCQdnBfr/I19b4y8PjD1qY762ztde/8wPTQZX9tcpkuGvrZrHADs2j/e/WzIvkzs+UbdWp89GVpwOoob6uuuerhrnfNLfYOXw3GzSWgCgWQmk7JalxtzZLB6BGOJ3OHeuZsJn97W2FKdOX5qvNJdmiXHZ3/Yn0rpRCQQzSbNSfedz9RvWrg5HokpmgEApGApc8HiqqirK/3GQMvS/hhYCECGdzj3+3cZWb6avf8LjdGy4oXlkKnv8bPTSg5PxZzKS9p1LHZX/YeKDnw4xeVIkRFSORKZ2EkT8Kkz0N/ZGbB41DY3VNyc3+8upC7MlMRKZKV6EjOE2vk6xK2z7yeEMPlugbpoCdAzDdqdKnvnd49AQBgt9u1Df2Ct1gsqizLeNovNhp0+C2OA8koaQnp9/rO2/aKxSaD7qM0c2S9LTfqSPVL+g7gdLk3R4Lvn7+mOzy/opoQygzl5NQIq0/p5lhK0e2LzTzqGkWc+MfHZXRCoZDRfINvaOwiz6hElTDSJI1SP3BSkjGC9pRbIp/87qt+t6PBqkEYVgcUzn9CAABxl/mB7nH0vYi07reLMYozcWJtqzI2u8KnIVC0eTcdVgg//uLewJtFRfvcQCkKR1Bh/zeUZYrtdqSVVnXmdI4JjvQEzWUyIPV+s7p1f5Zk8HkDQ5a8h0/4lTsdTtiCWifdzGoFQylFZ2t+TNl1tN2TVdJW99ddpChfbuVZGXiXku/4WVeK/MlA9GqOFK+HGgnWaVXKgvnXjSkLjWEYhmEYhmEYhmEYhmH+sz8BzQDdMcl1yrQAAAAASUVORK5CYII="

# ── Directories ───────────────────────────────────────────────────────────────
def get_template_dir():
    """Template directory for user-uploaded Excel templates."""
    d = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_templates")
    try:
        os.makedirs(d, exist_ok=True)
    except PermissionError:
        d = "/tmp/user_templates"
        os.makedirs(d, exist_ok=True)
    return d


def get_logo_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "excel_logo.png")


# ── Security Decorators ───────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.path.startswith(WS_PREFIX):
            return f(*args, **kwargs)
        if not session.get("authenticated"):
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "error": "Session expired. Please refresh and log in again."}), 401
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.path.startswith(WS_PREFIX):
                return f(*args, **kwargs)
            if not session.get("authenticated"):
                if request.path.startswith("/api/"):
                    return jsonify({"success": False, "error": "Session expired. Please log in."}), 401
                return redirect(url_for("auth.login"))
            user_role = session.get("role", "viewer")
            if user_role != 'admin' and user_role not in roles:
                if request.path.startswith("/api/"):
                    return jsonify({"success": False, "error": "غير مصرح لك (Forbidden)"}), 403
                from flask import abort
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ── Branch helpers ────────────────────────────────────────────────────────────
def is_workstation():
    """Determined purely by the URL prefix — never by the session."""
    return request.path.startswith(WS_PREFIX)


def current_branch_id():
    """Active branch id from the session (defaults to الدمام = 1)."""
    try:
        bid = int(session.get("branch_id", 1))
    except (TypeError, ValueError, RuntimeError):
        return 1
    return bid if bid in BRANCH_IDS else 1


def current_branch_name():
    return BRANCH_NAME.get(current_branch_id(), "الدمام")


def _row_id():
    return 2 if is_workstation() else current_branch_id()


# ── Table name validation ────────────────────────────────────────────────────
def _safe_tbl(table):
    """Validate table names to prevent SQL injection via identifier interpolation."""
    if not isinstance(table, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table):
        raise ValueError("invalid table name: %r" % (table,))
    return table


# ── JSON blob storage (branch-isolated via AppSetting) ────────────────────────
def _loads_blob(data_str):
    """Parse a blob row's JSON, tolerating corrupt/invalid data instead of raising 500."""
    if not data_str:
        return None
    try:
        return json.loads(data_str)
    except (ValueError, TypeError):
        logger.warning("Corrupt JSON blob encountered; returning None")
        return None


def blob_get(table):
    """Read JSON blob for the active branch from SQLAlchemy AppSetting."""
    from models.schema import AppSetting
    table = _safe_tbl(table)
    rid = _row_id()
    key = f"{table}_branch_{rid}"
    setting = AppSetting.query.get(key)
    return _loads_blob(setting.value) if setting else None


def blob_set(table, data_obj):
    """Write JSON blob for the active branch to SQLAlchemy AppSetting."""
    from models.schema import AppSetting, db
    data_obj = sanitize_data(data_obj)
    table = _safe_tbl(table)
    rid = _row_id()
    key = f"{table}_branch_{rid}"
    data_str = json.dumps(data_obj, ensure_ascii=False)

    try:
        setting = AppSetting.query.get(key)
        if setting:
            setting.value = data_str
        else:
            setting = AppSetting(key=key, value=data_str)
            db.session.add(setting)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving blob {key}: {e}")

    _snapshot(table, data_str)


def _global_blob_get(table):
    from models.schema import AppSetting
    table = _safe_tbl(table)
    key = f"{table}_global"
    setting = AppSetting.query.get(key)
    return _loads_blob(setting.value) if setting else None


def _global_blob_set(table, data_obj):
    from models.schema import AppSetting, db
    data_obj = sanitize_data(data_obj)
    table = _safe_tbl(table)
    key = f"{table}_global"
    data_str = json.dumps(data_obj, ensure_ascii=False)

    try:
        setting = AppSetting.query.get(key)
        if setting:
            setting.value = data_str
        else:
            setting = AppSetting(key=key, value=data_str)
            db.session.add(setting)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving global blob {key}: {e}")


# ── Data sanitization ────────────────────────────────────────────────────────
def sanitize_data(data):
    """Recursively strip excess whitespace from string values."""
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(v) for v in data]
    elif isinstance(data, str):
        return " ".join(data.split()).strip()
    return data


# ── Snapshot system ───────────────────────────────────────────────────────────
def _snapshot(table, data_str):
    """Append a dated snapshot using SQLAlchemy Snapshot model."""
    from models.schema import Snapshot, db
    if table not in SNAPSHOT_TABLES:
        return
    mode = _row_id()
    try:
        last = Snapshot.query.filter_by(tab=table, branch_id=mode).order_by(Snapshot.id.desc()).first()
        if last and last.data == data_str:
            return
        new_snap = Snapshot(tab=table, branch_id=mode, data=data_str)
        db.session.add(new_snap)
        snaps = Snapshot.query.filter_by(tab=table, branch_id=mode).order_by(Snapshot.id.desc()).all()
        if len(snaps) > SNAP_KEEP:
            for s in snaps[SNAP_KEEP:]:
                db.session.delete(s)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.warning("snapshot failed for %s: %s", table, e)


def _snapshot_list(tab, mode):
    from models.schema import Snapshot
    snaps = Snapshot.query.filter_by(tab=tab, branch_id=mode).order_by(Snapshot.id.desc()).all()
    return [{"id": s.id, "ts": s.timestamp.strftime('%Y-%m-%d %H:%M:%S') if s.timestamp else ""} for s in snaps]


def _restore_snapshot(sid, mode, require_tab=None):
    """Restore one dated snapshot into its tab's blob. Returns (ok, info)."""
    from models.schema import Snapshot
    snap = Snapshot.query.filter_by(id=sid, branch_id=mode).first()
    if not snap:
        return False, "not_found"
    if require_tab is not None and snap.tab != require_tab:
        return False, "tab_mismatch"
    try:
        data = json.loads(snap.data)
    except (ValueError, TypeError):
        return False, "corrupt"
    blob_set(snap.tab, data)
    _audit_add("استعادة نسخة", SNAP_LABELS.get(snap.tab, snap.tab), None, "من سجل النسخ المؤرّخة")
    return True, snap.tab


# ── Audit log ─────────────────────────────────────────────────────────────────
def _audit_get():
    from models.schema import AppSetting
    rid = _row_id()
    key = f"audit_log_branch_{rid}"
    setting = AppSetting.query.get(key)
    if not setting:
        return []
    try:
        return json.loads(setting.value) or []
    except Exception:
        return []


def _audit_write(log):
    from models.schema import AppSetting, db
    rid = _row_id()
    key = f"audit_log_branch_{rid}"
    data_str = json.dumps(log[-AUDIT_MAX:], ensure_ascii=False)
    try:
        setting = AppSetting.query.get(key)
        if setting:
            setting.value = data_str
        else:
            setting = AppSetting(key=key, value=data_str)
            db.session.add(setting)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving audit log: {e}")


def _audit_add(action, target, count=None, detail=""):
    """Best-effort audit entry. A logging failure must NEVER break the underlying save."""
    try:
        who = "محطة العمل" if is_workstation() else ((session.get("google_user") or {}).get("name") or "النظام")
        now = datetime.now()
        log = _audit_get()
        last = log[-1] if log else None
        if last and last.get("action") == action and last.get("target") == target and last.get("user") == who:
            try:
                delta = (now - datetime.strptime(last["ts"], "%Y-%m-%d %H:%M:%S")).total_seconds()
            except Exception:
                delta = AUDIT_COALESCE_SEC + 1
            if 0 <= delta <= AUDIT_COALESCE_SEC:
                last["ts"] = now.strftime("%Y-%m-%d %H:%M:%S")
                last["count"] = count
                last["detail"] = detail
                last["hits"] = last.get("hits", 1) + 1
                _audit_write(log)
                return
        log.append({
            "ts": now.strftime("%Y-%m-%d %H:%M:%S"),
            "user": who, "action": action, "target": target,
            "count": count, "detail": detail, "hits": 1,
        })
        _audit_write(log)
    except Exception:
        logger.exception("audit_add failed")


def audit_and_verify(action, target, reason):
    """يتحقق من وجود سبب وتضيفه لسجل التدقيق."""
    if not reason or len(reason.strip()) < 5:
        raise ValueError("يجب إدخال مسوّغ مكتوب (السبب) لإتمام التعديل.")
    _audit_add(action, target, detail=f"السبب: {reason.strip()}")
    return True


# ── System features ───────────────────────────────────────────────────────────
def get_system_features():
    d = _global_blob_get("system_features")
    if isinstance(d, dict):
        merged = dict(_DEFAULT_FEATURES)
        merged.update(d)
        return merged
    return dict(_DEFAULT_FEATURES)


def set_system_features(features):
    _global_blob_set("system_features", features)


# ── User/Account helpers ─────────────────────────────────────────────────────
def get_users():
    d = _global_blob_get("app_users")
    return d.get("users", []) if isinstance(d, dict) else []


def save_users(users):
    _global_blob_set("app_users", {"users": users})


def get_branch_accounts():
    d = _global_blob_get("branch_accounts")
    return d.get("accounts", []) if isinstance(d, dict) else []


def save_branch_accounts(accounts):
    _global_blob_set("branch_accounts", {"accounts": accounts})


# ── Logo loader ───────────────────────────────────────────────────────────────
def load_logo():
    b64_en = ""
    txt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "b64.txt")
    if os.path.exists(txt_path):
        with open(txt_path, "r") as f:
            content = f.read().strip()
            if not content.startswith("ar='") and not content.startswith("en='"):
                b64_en = content
    return b64_en
