import os
import json
import hmac
import logging
from flask import Blueprint, render_template, session, request, redirect, jsonify, current_app
from helpers import WS_PREFIX, _row_id, blob_get, blob_set, is_workstation, login_required, load_logo, _safe_tbl, _loads_blob
from models.database import db_connection
from models.schema import db, AppSetting

logger = logging.getLogger("InvoiceApp")
workstation_bp = Blueprint('workstation', __name__)

WORKSTATION_PASSWORD = os.environ.get("WORKSTATION_PASSWORD")
if not WORKSTATION_PASSWORD:
    import secrets
    WORKSTATION_PASSWORD = secrets.token_hex(16)

WS_TABS = {
    "": "index", "dashboard": "dashboard", "kpis": "kpis", "invoice": "index", "fleet_dashboard": "fleet_dashboard_new",
    "schedule": "schedule", "oils": "oils", "purchase": "purchase", "fuel": "fuel",
    "washing": "washing", "workshop": "workshop", "search": "search", "records": "records",
    "incidents": "incidents", "handover": "handover",
    "tracking": "tracking", "employees": "employees", "gps_sync": "gps_sync",
    "gps_dashboard": "gps_dashboard", "gps_devices": "gps_devices", "cameras": "cameras",
}
WS_LOCKED = {"employees", "gps_sync", "cameras", "tracking"}

# Fake sandbox data only — main site never uses this.
_HERE = os.path.dirname(__file__)
_WS_CANDIDATES = [
    os.path.join(_HERE, "ws_example_data.json"),
    os.path.join(_HERE, "..", "ws_example_data.json"),
    "/app/ws_example_data.json",
    "/app/routes/ws_example_data.json",
]
WS_EXAMPLE_PATH = next((p for p in _WS_CANDIDATES if os.path.isfile(p)), _WS_CANDIDATES[0])
try:
    with open(WS_EXAMPLE_PATH, encoding="utf-8") as _wsf:
        WS_EXAMPLE_DATA = json.load(_wsf)
except Exception as _e:
    logger.info("ws_example_data.json not loaded (optional sandbox file): %s", _e)
    WS_EXAMPLE_DATA = {}


def _ws_meta_get(k):
    key = f"ws_meta_{k}"
    setting = AppSetting.query.get(key)
    return setting.value if setting else None


def _ws_meta_set(k, v):
    key = f"ws_meta_{k}"
    try:
        setting = AppSetting.query.get(key)
        if setting:
            setting.value = str(v)
        else:
            setting = AppSetting(key=key, value=str(v))
            db.session.add(setting)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving ws_meta {key}: {e}")


def _ws_get2(table):
    """Read the workstation (id=2) blob for a table, or None."""
    table = _safe_tbl(table)
    key = f"{table}_branch_2"
    setting = AppSetting.query.get(key)
    return _loads_blob(setting.value) if setting else None


def _ws_put2(table, value):
    """Upsert the workstation (id=2) blob for a table."""
    table = _safe_tbl(table)
    key = f"{table}_branch_2"
    data_str = json.dumps(value, ensure_ascii=False)
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
        logger.error(f"Error saving ws blob {key}: {e}")


def _ws_is_empty(value):
    if value is None:
        return True
    if isinstance(value, list):
        return len(value) == 0
    if isinstance(value, dict):
        for v in value.values():
            if isinstance(v, list) and len(v) > 0:
                return False
        return True
    return False


def _ws_write_examples():
    for table, value in WS_EXAMPLE_DATA.items():
        _ws_put2(table, value)


def ensure_ws_seeded():
    try:
        if _ws_meta_get("ws_cleared") == "1":
            return
        for table, value in WS_EXAMPLE_DATA.items():
            if _ws_is_empty(_ws_get2(table)):
                _ws_put2(table, value)
    except Exception:
        logger.exception("ensure_ws_seeded error")


@workstation_bp.route(WS_PREFIX)
@workstation_bp.route(WS_PREFIX + "/<path:sub>")
def workstation_page(sub=""):
    ensure_ws_seeded()
    seg = sub.strip("/").split("/")[0] if sub else ""
    if seg == "api":
        return ("", 404)
    if seg not in WS_TABS:
        return redirect(WS_PREFIX)
    if seg in WS_LOCKED and not session.get("ws_unlocked"):
        return render_template("tab_lock.html", next=WS_PREFIX + "/" + seg)
    ctx = {"google_user": {"name": "Workstation", "email": "ws@system.local"}, "b64_en": load_logo()}
    if seg == "cameras":
        ctx["cameras_url"] = os.environ.get("CAMERAS_URL", "")
    if seg == "fleet_dashboard":
        branches = []
        try:
            with db_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT id, name FROM erp_branches")
                branches = [{"id": r[0], "name": r[1]} for r in c.fetchall()]
        except Exception:
            logger.exception("workstation fleet dashboard branches failed")
        insights = {"fleet": {"drivers": 0, "with_vehicle": 0, "without_vehicle": 0, "vehicles": 0},
                    "volume": {"employees": 0, "workshop": 0, "oils": 0, "purchase": 0, "gps_devices": 0},
                    "score": {"value": 0, "label": "غير متاح"},
                    "documents": {"expired": 0, "d30": 0}, "documents_top": [],
                    "generated_at": "—"}
        try:
            insight_view = current_app.view_functions.get("api_insights")
            if insight_view:
                response = insight_view()
                payload = response[0] if isinstance(response, tuple) else response
                data = payload.get_json(silent=True) if hasattr(payload, "get_json") else None
                if data and data.get("success"):
                    insights = data["insights"]
        except Exception:
            logger.exception("workstation fleet dashboard insights failed")
        ctx.update(branches=branches, is_admin=False, insights=insights)
    return render_template(WS_TABS[seg] + ".html", **ctx)


@workstation_bp.route(WS_PREFIX + "/unlock", methods=["POST"])
def workstation_unlock():
    from app import app
    nxt = request.form.get("next", WS_PREFIX)
    if not nxt.startswith(WS_PREFIX):
        nxt = WS_PREFIX
    if hmac.compare_digest(request.form.get("password", ""), WORKSTATION_PASSWORD):
        session["ws_unlocked"] = True
        resp = redirect(nxt)
        resp.set_cookie("ws_unlocked", "1", path=WS_PREFIX, samesite="Lax",
                        httponly=True,
                        secure=app.config.get("SESSION_COOKIE_SECURE", False))
        return resp
    return render_template("tab_lock.html", next=nxt, error="كلمة المرور غير صحيحة")

@workstation_bp.route("/api/ws_reset", methods=["POST"])
@login_required
def ws_reset():
    if not is_workstation():
        return jsonify({"success": False, "error": "workstation only"}), 404
    try:
        AppSetting.query.filter(AppSetting.key.like('%_branch_2')).delete(synchronize_session=False)
        db.session.commit()
        _ws_meta_set("ws_cleared", "1")
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        logger.exception(f"ws_reset error: {e}")
        return jsonify({"success": False}), 500


@workstation_bp.route("/api/ws_seed", methods=["POST"])
@login_required
def ws_seed():
    if not is_workstation():
        return jsonify({"success": False, "error": "workstation only"}), 404
    try:
        _ws_write_examples()
        _ws_meta_set("ws_cleared", "0")
        return jsonify({"success": True})
    except Exception:
        logger.exception("ws_seed error")
        return jsonify({"success": False}), 500
