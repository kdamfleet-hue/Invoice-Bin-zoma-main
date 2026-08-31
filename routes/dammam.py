import json
import os
from flask import render_template, session, jsonify
from helpers import login_required, load_logo
from routes.operations import operations_bp

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "data", "dammam_vehicles_73.json")
BLOB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "data", "dammam_73.txt")

def _notes(status, lic_st, insp_st):
    notes = []
    if status and status not in ("صالحة", "سليم - جاهز للعمل"):
        notes.append(status)
    if lic_st and lic_st not in ("ساري",):
        notes.append("رخصة السير: " + lic_st)
    if insp_st and insp_st not in ("ساري",):
        notes.append("الفحص: " + insp_st)
    return " — ".join(notes) if notes else "لا توجد ملاحظات"

def _parse_blob(text):
    rows = []
    for line in (text or "").strip().splitlines():
        p = line.split("|")
        if len(p) < 15:
            continue
        rows.append({
            "n": int(p[0]), "plate": p[1], "reg_type": p[2], "make": p[3], "model": p[4],
            "year": p[5], "serial": p[6], "chassis": p[7], "status": p[8],
            "lic_hijri": p[9], "lic_greg": p[10], "lic_status": p[11],
            "insp_hijri": p[12], "insp_greg": p[13], "insp_status": p[14],
            "notes": _notes(p[8], p[11], p[14]),
        })
    return rows

def load_vehicles():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            rows = [r for r in json.load(f) if str(r.get("plate") or "").strip()]
        if len(rows) >= 73:
            return rows
    except Exception:
        pass
    try:
        with open(BLOB_PATH, "r", encoding="utf-8") as f:
            rows = _parse_blob(f.read())
        if rows:
            return rows
    except Exception:
        pass
    return []

@operations_bp.route("/dammam")
@login_required
def dammam_vehicles():
    return render_template("dammam_vehicles.html", google_user=session.get("google_user"), b64_en=load_logo(), vehicles=load_vehicles())

@operations_bp.route("/dammam/v/<int:n>")
@login_required
def dammam_vehicle_unit(n):
    items = load_vehicles()
    item = next((x for x in items if int(x.get("n") or 0) == n), None)
    if not item and 1 <= n <= len(items):
        item = items[n - 1]
    return render_template("dammam_vehicle_unit.html", google_user=session.get("google_user"), b64_en=load_logo(), v=item, vehicles=items)

@operations_bp.route("/api/dammam_vehicles")
@login_required
def api_dammam_vehicles():
    return jsonify(load_vehicles())

@operations_bp.route("/api/drivers")
@login_required
def api_drivers_alias():
    try:
        from models.schema import Driver, Vehicle, VehicleCustody
        from helpers import current_branch_id
        branch_id = current_branch_id()
        q = Driver.query
        if branch_id:
            q = q.filter_by(branch_id=branch_id)
        drivers = q.all()
        vehicles = {v.id: v for v in Vehicle.query.all()}
        custodies = VehicleCustody.query.filter_by(status="active").all()
        driver_custody = {c.driver_id: c for c in custodies}
        data = []
        for d in drivers:
            c = driver_custody.get(d.id)
            v = vehicles.get(c.vehicle_id) if c else None
            data.append({"id": d.id, "name": d.name or "", "phone": d.phone or "", "job": d.job_title or "", "plate": (v.plate_number if v else "") or "", "car": (v.v_type if v else "") or ""})
        return jsonify(data)
    except Exception:
        return jsonify([])

@operations_bp.route("/purchase/list")
@login_required
def purchase_list():
    return render_template("purchase_list.html", google_user=session.get("google_user"), b64_en=load_logo())


def dammam_plate_set():
    from helpers import normalize_plate
    return {normalize_plate(v.get("plate")) for v in load_vehicles() if v.get("plate")}

def dammam_rows_by_plate():
    from helpers import normalize_plate
    out = {}
    for v in load_vehicles():
        k = normalize_plate(v.get("plate"))
        if k:
            out[k] = v
    return out
