import logging
from flask import Blueprint, render_template, session, request, jsonify
from helpers import login_required, load_logo, blob_get, blob_set, audit_and_verify

logger = logging.getLogger("InvoiceApp")
operations_bp = Blueprint('operations', __name__)

@operations_bp.route("/oils")
@login_required
def oils():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("oils.html", google_user=google_user, b64_en=b64_en)

@operations_bp.route("/fuel")
@login_required
def fuel():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("fuel.html", google_user=google_user, b64_en=b64_en)

@operations_bp.route("/purchase")
@login_required
def purchase():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("purchase.html", google_user=google_user, b64_en=b64_en)

@operations_bp.route("/workshop")
@login_required
def workshop():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("workshop.html", google_user=google_user, b64_en=b64_en,
                           kiosk=bool(session.get("kiosk")))

@operations_bp.route("/api/oils_data", methods=["GET", "POST"])
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

@operations_bp.route("/api/fuel_data", methods=["GET", "POST"])
@login_required
def fuel_data():
    if request.method == "POST":
        try:
            entries = (request.json or {}).get("entries", [])
            blob_set("fuel_data", entries)
            _audit_add("تحديث", "تموين المحروقات", len(entries) if isinstance(entries, list) else None)
            return jsonify({"success": True})
        except Exception:
            logger.exception("fuel_data POST error")
            return jsonify({"success": False, "error": "تعذّر حفظ بيانات التموين."}), 500
    try:
        data = blob_get("fuel_data")
        return jsonify({"success": True, "entries": data if isinstance(data, list) else []})
    except Exception:
        logger.exception("fuel_data GET error")
        return jsonify({"success": False, "entries": []})

@operations_bp.route("/api/purchase_data", methods=["GET", "POST"])
@login_required
def purchase_data():
    if request.method == "POST":
        try:
            body = request.json or {}
            blob_set("purchase_data", body)
            _n = sum(len(v) for v in body.values() if isinstance(v, list)) if isinstance(body, dict) else None
            _audit_add("تحديث", "طلبات الشراء", _n or None)
            return jsonify({"success": True})
        except Exception:
            logger.exception("purchase_data POST error")
            return jsonify({"success": False}), 500
    try:
        return jsonify({"success": True, "data": blob_get("purchase_data")})
    except Exception:
        logger.exception("purchase_data GET error")
        return jsonify({"success": False, "data": None})

@operations_bp.route("/api/workshop_data", methods=["GET", "POST"])
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