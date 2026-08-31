"""Operational fleet cycle: daily / weekly / garage — no deletion of existing data."""
from datetime import datetime, timedelta
from flask import render_template, session, request, jsonify
from helpers import login_required, load_logo, blob_get, blob_set, _audit_add, current_branch_id
from routes.operations import operations_bp

PM_INTERVAL_KM = 10000
PM_WARN_KM = 9000
STD_KML = 3.2


def _now():
    return datetime.now()


def _parse_date(val):
    if not val:
        return None
    s = str(val).strip()[:10]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _num(val):
    try:
        digits = "".join(ch if ch.isdigit() or ch == "." else "" for ch in str(val or ""))
        return float(digits) if digits else 0.0
    except Exception:
        return 0.0


def _dammam_catalog():
    try:
        from routes.dammam import load_vehicles
        return load_vehicles() or []
    except Exception:
        return []


def _fuel_rows():
    data = blob_get("fuel_data")
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    if isinstance(data, dict):
        rows = data.get("entries") or data.get("rows") or []
        return [r for r in rows if isinstance(r, dict)]
    return []


def _workshop_rows():
    data = blob_get("workshop_data")
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("rows") or data.get("orders") or []
    return []


def _readiness():
    catalog = _dammam_catalog()
    yard = blob_get("yard_board") or {}
    columns = yard.get("columns") if isinstance(yard, dict) else {}
    ready = in_ws = parked = on_road = 0
    if isinstance(columns, dict):
        ready = len(columns.get("جاهزة") or columns.get("ready") or [])
        in_ws = len(columns.get("صيانة") or columns.get("workshop") or [])
        parked = len(columns.get("موقفة") or columns.get("parked") or [])
        on_road = len(columns.get("خارج") or columns.get("road") or [])
    total = len(catalog) or (ready + in_ws + parked + on_road)
    return {
        "total": total,
        "ready": ready,
        "workshop": in_ws,
        "parked": parked,
        "road": on_road,
        "active_pct": round(100 * ready / total, 1) if total else 0,
        "down_pct": round(100 * in_ws / total, 1) if total else 0,
    }


def _fuel_efficiency():
    by_plate = {}
    for r in _fuel_rows():
        plate = str(r.get("plate") or "").strip()
        if not plate:
            continue
        liters = _num(r.get("liters") or r.get("qty"))
        prev_odo = _num(r.get("prevOdo") or r.get("prev_odo"))
        cur_odo = _num(r.get("curOdo") or r.get("current_odo") or r.get("odo"))
        km = max(0, cur_odo - prev_odo) if cur_odo and prev_odo else 0
        rec = by_plate.setdefault(plate, {"plate": plate, "liters": 0, "km": 0, "cost": 0, "driver": r.get("driver") or ""})
        rec["liters"] += liters
        rec["km"] += km
        rec["cost"] += _num(r.get("cost") or r.get("amount"))
        if r.get("driver"):
            rec["driver"] = r.get("driver")
    out = []
    for rec in by_plate.values():
        kml = (rec["km"] / rec["liters"]) if rec["liters"] else 0
        rec["kml"] = round(kml, 2)
        rec["flag"] = "فحص" if (kml and kml < STD_KML) else "ضمن المعيار"
        rec["std"] = STD_KML
        out.append(rec)
    out.sort(key=lambda x: x["kml"] or 99)
    return out


def _pm_due():
    catalog = _dammam_catalog()
    oils = blob_get("oils_data") or []
    last_oil = {}
    rows = oils.get("rows") if isinstance(oils, dict) else (oils if isinstance(oils, list) else [])
    for row in rows:
        plate, odo = "", 0
        if isinstance(row, dict):
            plate = str(row.get("plate") or "").strip()
            odo = int(_num(row.get("counter") or row.get("odo") or row.get("km")))
        elif isinstance(row, list) and len(row) > 3:
            plate = str(row[0] or "").strip()
            odo = int(_num(row[3]))
        if plate:
            last_oil[plate] = max(last_oil.get(plate, 0), odo)
    due = []
    try:
        from models.schema import Vehicle
        vehicles = {(v.plate_number or "").strip(): v for v in Vehicle.query.all()}
    except Exception:
        vehicles = {}
    for item in catalog:
        plate = (item.get("plate") or "").strip()
        v = vehicles.get(plate)
        current = int(getattr(v, "current_km", 0) or getattr(v, "odometer", 0) or 0) if v else 0
        base = last_oil.get(plate, 0)
        delta = current - base if current else 0
        remaining = PM_INTERVAL_KM - delta if current else None
        if remaining is None:
            continue
        if remaining <= (PM_INTERVAL_KM - PM_WARN_KM):
            due.append({
                "plate": plate,
                "make": item.get("make"),
                "model": item.get("model"),
                "current_km": current,
                "last_service_km": base,
                "remaining_km": remaining,
                "status": "تجاوز الحد" if remaining <= 0 else "خلال الأسبوع",
            })
    due.sort(key=lambda x: x["remaining_km"])
    return due


def _work_orders():
    stored = blob_get("work_orders_cycle")
    if isinstance(stored, list):
        return stored
    derived = []
    for i, row in enumerate(_workshop_rows(), start=1):
        if isinstance(row, dict):
            derived.append({
                "id": row.get("id") or i,
                "plate": row.get("plate") or row.get("car") or "",
                "type": row.get("type") or "علاجية",
                "status": row.get("status") or "مفتوح",
                "opened": row.get("date") or row.get("entry") or "",
                "closed": row.get("exit") or "",
                "cost": row.get("cost") or 0,
                "issue": row.get("issue") or row.get("notes") or "",
            })
        elif isinstance(row, list) and row:
            derived.append({
                "id": i,
                "plate": row[0] if len(row) > 0 else "",
                "type": "علاجية",
                "status": row[4] if len(row) > 4 else "مفتوح",
                "opened": row[1] if len(row) > 1 else "",
                "closed": row[2] if len(row) > 2 else "",
                "cost": row[8] if len(row) > 8 else 0,
                "issue": row[3] if len(row) > 3 else "",
            })
    return derived


def _mttr(orders):
    durations = []
    repeats = {}
    open_n = 0
    for o in orders:
        st = str(o.get("status") or "")
        if st in ("مفتوح", "قيد التنفيذ", "انتظار"):
            open_n += 1
        a, b = _parse_date(o.get("opened")), _parse_date(o.get("closed"))
        if a and b and b >= a:
            durations.append((b - a).total_seconds() / 3600)
        plate = str(o.get("plate") or "").strip()
        if plate:
            repeats[plate] = repeats.get(plate, 0) + 1
    avg = round(sum(durations) / len(durations), 1) if durations else 0
    repeat_n = sum(1 for n in repeats.values() if n >= 2)
    return {
        "open": open_n,
        "closed": max(0, len(orders) - open_n),
        "mttr_hours": avg,
        "repeat_vehicles": repeat_n,
        "repeat_rate": round(100 * repeat_n / max(len(repeats), 1), 1),
    }


@operations_bp.route("/ops")
@login_required
def ops_cycle_page():
    return render_template(
        "ops_cycle.html",
        google_user=session.get("google_user"),
        b64_en=load_logo(),
        pm_interval=PM_INTERVAL_KM,
        std_kml=STD_KML,
    )


@operations_bp.route("/api/ops/summary")
@login_required
def ops_summary():
    orders = _work_orders()
    fuel = _fuel_efficiency()
    pm = _pm_due()
    checks = blob_get("pretrip_checks") or []
    today = _now().strftime("%Y-%m-%d")
    today_checks = [c for c in checks if isinstance(c, dict) and str(c.get("date")) == today]
    return jsonify({
        "success": True,
        "readiness": _readiness(),
        "workshop": _mttr(orders),
        "fuel_alerts": [f for f in fuel if f.get("flag") == "فحص"][:12],
        "pm_due": pm[:20],
        "today_checks": len(today_checks),
        "today_faults": sum(1 for c in today_checks if c.get("fault")),
        "generated_at": _now().strftime("%Y-%m-%d %H:%M"),
        "scope": "فرع الدمام — عرض تشغيلي دون مسح البيانات",
    })


@operations_bp.route("/api/ops/pretrip", methods=["GET", "POST"])
@login_required
def ops_pretrip():
    checks = blob_get("pretrip_checks") or []
    if not isinstance(checks, list):
        checks = []
    if request.method == "GET":
        plate = (request.args.get("plate") or "").strip()
        rows = [c for c in checks if not plate or str(c.get("plate")) == plate]
        return jsonify({"success": True, "rows": list(reversed(rows[-200:]))})
    body = request.json or {}
    plate = str(body.get("plate") or "").strip()
    if not plate:
        return jsonify({"success": False, "error": "رقم اللوحة مطلوب"}), 400
    rec = {
        "id": int(_now().timestamp() * 1000),
        "date": _now().strftime("%Y-%m-%d"),
        "time": _now().strftime("%H:%M"),
        "plate": plate,
        "driver": str(body.get("driver") or "").strip(),
        "oil": bool(body.get("oil")),
        "tires": bool(body.get("tires")),
        "lights": bool(body.get("lights")),
        "odo": int(_num(body.get("odo"))),
        "gps_odo": int(_num(body.get("gps_odo"))),
        "fault": str(body.get("fault") or "").strip(),
        "ok": not str(body.get("fault") or "").strip() and bool(body.get("oil")) and bool(body.get("tires")) and bool(body.get("lights")),
    }
    if rec["gps_odo"] and rec["odo"] and abs(rec["gps_odo"] - rec["odo"]) > 25:
        rec["odo_mismatch"] = True
    checks.append(rec)
    blob_set("pretrip_checks", checks[-800:])
    _audit_add("فحص يومي", plate, None, rec.get("fault") or "سليم")
    if rec.get("fault"):
        try:
            from models.schema import Vehicle, WorkshopRecord, db
            v = Vehicle.query.filter(Vehicle.plate_number.like(f"%{plate}%")).first()
            if v:
                open_wo = WorkshopRecord.query.filter_by(vehicle_id=v.id, status="مفتوح").first()
                if not open_wo:
                    db.session.add(WorkshopRecord(
                        vehicle_id=v.id,
                        entry_date=_now().date(),
                        issue_description=rec["fault"],
                        status="مفتوح",
                    ))
                    db.session.commit()
        except Exception:
            pass
    return jsonify({"success": True, "row": rec})


@operations_bp.route("/api/ops/work_orders", methods=["GET", "POST"])
@login_required
def ops_work_orders():
    orders = _work_orders()
    if request.method == "GET":
        return jsonify({"success": True, "rows": orders, "kpis": _mttr(orders)})
    body = request.json or {}
    action = body.get("action") or "open"
    if action == "open":
        plate = str(body.get("plate") or "").strip()
        if not plate:
            return jsonify({"success": False, "error": "اللوحة مطلوبة"}), 400
        rec = {
            "id": int(_now().timestamp() * 1000),
            "plate": plate,
            "type": body.get("type") or "علاجية",
            "status": "مفتوح",
            "opened": _now().strftime("%Y-%m-%d"),
            "closed": "",
            "cost": _num(body.get("cost")),
            "issue": str(body.get("issue") or "").strip(),
            "mechanic": str(body.get("mechanic") or "").strip(),
        }
        stored = blob_get("work_orders_cycle")
        stored = stored if isinstance(stored, list) else []
        stored.append(rec)
        blob_set("work_orders_cycle", stored)
        _audit_add("فتح أمر شغل", plate, None, rec["issue"])
        return jsonify({"success": True, "row": rec})
    if action in ("progress", "close", "ready"):
        oid = body.get("id")
        stored = blob_get("work_orders_cycle")
        stored = stored if isinstance(stored, list) else orders
        for rec in stored:
            if str(rec.get("id")) == str(oid):
                rec["status"] = "قيد التنفيذ" if action == "progress" else ("جاهزة للتشغيل" if action == "ready" else "مغلق")
                if action in ("close", "ready"):
                    rec["closed"] = _now().strftime("%Y-%m-%d")
                    rec["cost"] = _num(body.get("cost") or rec.get("cost"))
                blob_set("work_orders_cycle", stored)
                _audit_add("تحديث أمر شغل", rec.get("plate") or "", None, rec["status"])
                return jsonify({"success": True, "row": rec})
        return jsonify({"success": False, "error": "الأمر غير موجود"}), 404
    return jsonify({"success": False, "error": "إجراء غير معروف"}), 400


@operations_bp.route("/api/ops/idle", methods=["GET", "POST"])
@login_required
def ops_idle():
    rows = blob_get("idle_events") or []
    if not isinstance(rows, list):
        rows = []
    if request.method == "POST":
        body = request.json or {}
        rec = {
            "id": int(_now().timestamp() * 1000),
            "date": _now().strftime("%Y-%m-%d"),
            "plate": str(body.get("plate") or "").strip(),
            "hours": _num(body.get("hours")),
            "note": str(body.get("note") or "").strip(),
        }
        if not rec["plate"]:
            return jsonify({"success": False, "error": "اللوحة مطلوبة"}), 400
        rows.append(rec)
        blob_set("idle_events", rows[-400:])
        return jsonify({"success": True, "row": rec})
    week = (_now() - timedelta(days=7)).strftime("%Y-%m-%d")
    recent = [r for r in rows if isinstance(r, dict) and str(r.get("date") or "") >= week]
    total_h = sum(_num(r.get("hours")) for r in recent)
    return jsonify({"success": True, "rows": recent, "week_hours": round(total_h, 1)})
