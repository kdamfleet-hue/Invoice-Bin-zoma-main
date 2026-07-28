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
            _sync_purchase_inventory(body)
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
        return jsonify({"success": False, "data": None}), 500

def _sync_purchase_inventory(body):
    try:
        from models.schema import TireRecord, BatteryRecord, Vehicle, db
        from helpers import current_branch_id
        if not isinstance(body, dict):
            return
        
        tires_list = body.get("tires") or []
        batteries_list = body.get("batteries") or []
        po_plate = (body.get("poPlate") or body.get("plate") or "").strip()

        v = None
        if po_plate:
            v = Vehicle.query.filter(Vehicle.plate_number.like(f"%{po_plate}%")).first()

        b_id = current_branch_id()

        for t_item in tires_list:
            if isinstance(t_item, dict):
                serial = str(t_item.get("serial") or t_item.get("serial_number") or "").strip()
                if serial:
                    existing = TireRecord.query.filter_by(serial_number=serial).first()
                    if not existing:
                        tr = TireRecord(
                            branch_id=b_id,
                            vehicle_id=v.id if v else None,
                            serial_number=serial,
                            brand=t_item.get("brand") or "Purchase Order",
                            size=t_item.get("size"),
                            status="جديد"
                        )
                        db.session.add(tr)

        for b_item in batteries_list:
            if isinstance(b_item, dict):
                serial = str(b_item.get("serial") or b_item.get("serial_number") or "").strip()
                if serial:
                    existing = BatteryRecord.query.filter_by(serial_number=serial).first()
                    if not existing:
                        br = BatteryRecord(
                            branch_id=b_id,
                            vehicle_id=v.id if v else None,
                            serial_number=serial,
                            brand=b_item.get("brand") or "Purchase Order",
                            capacity=b_item.get("amp") or b_item.get("capacity"),
                            status="نشط"
                        )
                        db.session.add(br)

        db.session.commit()
    except Exception:
        logger.exception("_sync_purchase_inventory error")
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
            data = request.json or {}
            blob_set("workshop_data", data)
            
            plate = data.get("car") or data.get("plate")
            if plate:
                from models.schema import Vehicle, WorkshopRecord, db
                from datetime import datetime
                v = Vehicle.query.filter_by(plate_number=plate).first()
                if v:
                    record = WorkshopRecord.query.filter_by(vehicle_id=v.id, status="مفتوح").first()
                    if not record:
                        record = WorkshopRecord(
                            vehicle_id=v.id,
                            entry_date=datetime.now().date(),
                            status="مفتوح"
                        )
                        db.session.add(record)
                    record.mechanic_name = data.get("driver", "")
                    record.issue_description = str(data.get("notes", ""))
                    db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            logger.exception(f"workshop_data POST error: {e}")
            return jsonify({"success": False}), 500
    try:
        return jsonify({"success": True, "data": blob_get("workshop_data")})
    except Exception:
        logger.exception("workshop_data GET error")
        return jsonify({"success": False, "data": None})

@operations_bp.route("/api/update_km", methods=["POST"])
@login_required
def update_km():
    """Universal endpoint to securely update a vehicle's odometer by plate in JSON blobs."""
    try:
        data = request.json or {}
        plate = str(data.get("plate", "")).strip()
        km_val = str(data.get("km", "")).strip()
        if not plate or not km_val:
            return jsonify({"success": False})

        km_int = int("".join(filter(str.isdigit, km_val)))
        updated = False
        
        # 1. Update employees blob (main source of truth for fleet)
        employees_blob = blob_get("employees")
        if employees_blob and isinstance(employees_blob, dict) and isinstance(employees_blob.get("data"), list):
            for row in employees_blob["data"]:
                if isinstance(row, dict) and str(row.get("plate", "")).strip() == plate:
                    old_km = str(row.get("odometer", row.get("km", row.get("current_km", ""))))
                    try:
                        old_km_int = int("".join(filter(str.isdigit, old_km))) if old_km.strip() else 0
                    except ValueError:
                        old_km_int = 0
                    if km_int > old_km_int:
                        row["odometer"] = km_int
                        row["current_km"] = km_int
                        row["km"] = km_int
                        updated = True
            if updated:
                blob_set("employees", employees_blob)
                
        # 2. Update schedule_data blob (secondary source of truth)
        schedule_blob = blob_get("schedule_data")
        sch_updated = False
        if schedule_blob and isinstance(schedule_blob, dict) and isinstance(schedule_blob.get("rows"), list):
            for row in schedule_blob["rows"]:
                if isinstance(row, dict) and str(row.get("plate", "")).strip() == plate:
                    old_km = str(row.get("odometer", row.get("km", "")))
                    try:
                        old_km_int = int("".join(filter(str.isdigit, old_km))) if old_km.strip() else 0
                    except ValueError:
                        old_km_int = 0
                    if km_int > old_km_int:
                        row["odometer"] = km_int
                        row["km"] = km_int
                        sch_updated = True
            if sch_updated:
                blob_set("schedule_data", schedule_blob)
                updated = True

        # 3. Update SQL Vehicle model if present
        try:
            from models.schema import db, Vehicle
            v = Vehicle.query.filter_by(plate_number=plate).first()
            if v and (v.current_km is None or km_int > v.current_km):
                v.current_km = km_int
                v.odometer = km_int
                db.session.commit()
                updated = True
        except Exception as e:
            logger.warning(f"SQL Vehicle update warning: {e}")

        if updated:
            logger.info(f"✅ Odometer updated for {plate}: {km_int}")
            return jsonify({"success": True})
    except ValueError:
        pass
    except Exception as e:
        logger.error(f"Failed to update KM in blobs: {e}")
    return jsonify({"success": False})

# --- SPARE PARTS & DISPENSING API ---
@operations_bp.route("/api/spare_parts", methods=["GET", "POST"])
@login_required
def api_spare_parts():
    from models.schema import SparePart, db
    if request.method == "POST":
        data = request.json or {}
        part = SparePart(
            branch_id=current_branch_id() or 1,
            part_number=data.get("part_number", "").strip(),
            name=data.get("name", "").strip(),
            category=data.get("category", "أخرى"),
            quantity=int(data.get("quantity", 0)),
            price=float(data.get("unit_price", data.get("price", 0))),
            supplier=data.get("supplier", "").strip()
        )
        db.session.add(part)
        db.session.commit()
        return jsonify({"success": True, "part": {"id": part.id, "name": part.name, "part_number": part.part_number, "quantity": part.quantity, "unit_price": float(part.price or 0), "category": part.category, "supplier": part.supplier}})
        
    parts = SparePart.query.all()
    res = []
    for p in parts:
        res.append({
            "id": p.id,
            "name": p.name,
            "part_number": p.part_number,
            "quantity": p.quantity,
            "unit_price": float(p.price or 0),
            "category": p.category,
            "supplier": p.supplier,
            "last_updated": p.last_updated.strftime("%Y-%m-%d %H:%M") if p.last_updated else ""
        })
    return jsonify(res)

@operations_bp.route("/api/spare_parts/<int:part_id>", methods=["PUT", "DELETE"])
@login_required
def api_spare_parts_manage(part_id):
    from models.schema import SparePart, db
    p = SparePart.query.get_or_404(part_id)
    if request.method == "DELETE":
        db.session.delete(p)
        db.session.commit()
        return jsonify({"success": True})
        
    data = request.json or {}
    if "name" in data: p.name = data["name"].strip()
    if "part_number" in data: p.part_number = data["part_number"].strip()
    if "category" in data: p.category = data["category"]
    if "quantity" in data: p.quantity = int(data["quantity"])
    if "unit_price" in data: p.price = float(data["unit_price"])
    if "supplier" in data: p.supplier = data["supplier"].strip()
    db.session.commit()
    return jsonify({"success": True})

@operations_bp.route("/api/dispense_part", methods=["POST"])
@login_required
def dispense_part():
    from models.schema import SparePart, Vehicle, WorkshopRecord, WorkshopPartUsage, db
    from datetime import datetime
    data = request.json or {}
    plate = data.get("plate")
    part_id = data.get("part_id")
    qty = int(data.get("quantity", 1))
    
    if not plate or not part_id:
        return jsonify({"success": False, "error": "Missing plate or part_id"})
        
    part = SparePart.query.get(part_id)
    if not part or part.quantity < qty:
        return jsonify({"success": False, "error": "Not enough inventory"})
        
    v = Vehicle.query.filter_by(plate_number=plate).first()
    if not v:
        return jsonify({"success": False, "error": "Vehicle not found"})
        
    record = WorkshopRecord.query.filter_by(vehicle_id=v.id, status="مفتوح").first()
    if not record:
        record = WorkshopRecord(vehicle_id=v.id, entry_date=datetime.now().date(), status="مفتوح")
        db.session.add(record)
        db.session.flush()
        
    usage = WorkshopPartUsage(workshop_record_id=record.id, spare_part_id=part.id, quantity_used=qty)
    part.quantity -= qty
    
    db.session.add(usage)
    db.session.commit()
    
    return jsonify({"success": True, "usage_id": usage.id, "remaining_quantity": part.quantity})

@operations_bp.route("/api/refund_part", methods=["POST"])
@login_required
def refund_part():
    from models.schema import SparePart, WorkshopPartUsage, db
    data = request.json or {}
    usage_id = data.get("usage_id")
    
    if not usage_id:
        return jsonify({"success": False, "error": "Missing usage_id"})
        
    usage = WorkshopPartUsage.query.get(usage_id)
    if not usage:
        return jsonify({"success": False, "error": "Usage record not found"})
        
    part = SparePart.query.get(usage.spare_part_id)
    if part:
        part.quantity += usage.quantity_used
        
    db.session.delete(usage)
    db.session.commit()
    
    return jsonify({"success": True, "remaining_quantity": part.quantity if part else 0})