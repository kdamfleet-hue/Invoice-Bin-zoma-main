import logging
from flask import Blueprint, render_template, request, jsonify, session
from helpers import login_required, role_required, load_logo, current_branch_id, _audit_add, blob_get, blob_set, normalize_plate

logger = logging.getLogger("InvoiceApp")
yard_bp = Blueprint("yard", __name__)

COLUMNS = {
    "out": {"status": "خارج الساحة", "condition": "على الطريق", "label": "خارج الساحة (على الطريق)"},
    "ready": {"status": "متواجد بالساحة", "condition": "جاهزة", "label": "جاهزة للعمل"},
    "maint": {"status": "متواجد بالساحة", "condition": "في الصيانة", "label": "في الصيانة"},
    "stopped": {"status": "متواجد بالساحة", "condition": "موقوفة", "label": "موقوفة / أعطال"},
}


def _col_of(status, condition):
    st = (status or "").strip()
    cd = (condition or "").strip()
    if st in ("خارج الساحة", "على الطريق", "") and cd in ("", "على الطريق", "غير محدد"):
        if "صيان" in cd:
            return "maint"
        if "موقوف" in cd or "عطل" in cd:
            return "stopped"
        if "جاهز" in cd:
            return "ready"
        if st in ("خارج الساحة", "على الطريق", ""):
            return "out"
    if "صيان" in cd or "صيان" in st:
        return "maint"
    if "موقوف" in cd or "عطل" in cd or "معطل" in st:
        return "stopped"
    if st == "خارج الساحة" or st == "على الطريق":
        return "out"
    return "ready"


def _board():
    data = blob_get("yard_board") or {}
    return data if isinstance(data, dict) else {}


def _save_board(board):
    blob_set("yard_board", board)


@yard_bp.route("/yard")
@login_required
@role_required("admin", "operations")
def yard_page():
    return render_template("yard.html", google_user=session.get("google_user"), b64_en=load_logo())


@yard_bp.route("/api/yard", methods=["GET"])
@login_required
def api_yard():
    from models.schema import Vehicle
    board = _board()
    vehicles = Vehicle.query.filter_by(branch_id=current_branch_id()).all()
    result = []
    seen = set()
    for v in vehicles:
        plate = (v.plate_number or "").strip()
        key = normalize_plate(plate)
        pos = board.get(key) or board.get(plate) or {}
        status = pos.get("status") or v.yard_status or "خارج الساحة"
        condition = pos.get("condition") or v.yard_condition or "غير محدد"
        result.append({
            "id": v.id,
            "key": key or str(v.id),
            "plate": plate,
            "type": v.v_type or v.model or "",
            "status": status,
            "condition": condition,
            "column": _col_of(status, condition),
        })
        if key:
            seen.add(key)

    try:
        from routes.dammam import load_vehicles
        for row in load_vehicles():
            plate = (row.get("plate") or "").strip()
            key = normalize_plate(plate)
            if not key or key in seen:
                continue
            pos = board.get(key) or board.get(plate) or {}
            status = pos.get("status") or "خارج الساحة"
            condition = pos.get("condition") or "غير محدد"
            result.append({
                "id": None,
                "key": key,
                "plate": plate,
                "type": " ".join(x for x in (row.get("make"), row.get("model"), row.get("year")) if x),
                "status": status,
                "condition": condition,
                "column": _col_of(status, condition),
            })
            seen.add(key)
    except Exception:
        logger.exception("yard dammam merge failed")

    return jsonify({"vehicles": result, "columns": COLUMNS})


@yard_bp.route("/api/yard/move", methods=["POST"])
@login_required
@role_required("admin", "operations")
def move_yard(extra=None):
    data = dict(request.json or {})
    if extra:
        data.update(extra)
    plate = (data.get("plate") or "").strip()
    vid = data.get("id")
    column = (data.get("column") or data.get("col") or "").strip()
    status = (data.get("status") or "").strip()
    condition = (data.get("condition") or "").strip()

    if column in COLUMNS:
        status = COLUMNS[column]["status"]
        condition = COLUMNS[column]["condition"]
    if not status:
        status = "خارج الساحة"
    if not condition:
        condition = "غير محدد"

    from models.schema import db, Vehicle
    v = None
    if vid:
        try:
            v = Vehicle.query.filter_by(id=int(vid), branch_id=current_branch_id()).first()
        except (TypeError, ValueError):
            v = None
    if not v and plate:
        v = Vehicle.query.filter(Vehicle.plate_number == plate, Vehicle.branch_id == current_branch_id()).first()
        if not v:
            like = f"%{plate}%"
            v = Vehicle.query.filter(Vehicle.plate_number.like(like), Vehicle.branch_id == current_branch_id()).first()

    if v:
        v.yard_status = status
        v.yard_condition = condition
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.exception("yard sql update failed")
            return jsonify({"success": False, "error": str(e)}), 400
        plate = v.plate_number or plate
        vid = v.id

    key = normalize_plate(plate) or str(vid or "")
    if not key:
        return jsonify({"success": False, "error": "لم يُحدد المركبة"}), 400

    board = _board()
    board[key] = {"status": status, "condition": condition, "plate": plate, "id": vid}
    _save_board(board)
    try:
        _audit_add("تحديث ساحة", plate or key, 1, f"{status} / {condition}")
    except Exception:
        pass
    return jsonify({"success": True, "status": status, "condition": condition, "id": vid, "plate": plate})


@yard_bp.route("/api/yard/<vehicle_id>", methods=["PUT"])
@login_required
@role_required("admin", "operations")
def update_yard(vehicle_id):
    extra = {}
    if str(vehicle_id).isdigit():
        extra["id"] = int(vehicle_id)
    else:
        extra["plate"] = vehicle_id
    return move_yard(extra)
