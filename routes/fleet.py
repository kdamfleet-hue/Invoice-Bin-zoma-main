import re
import json
import io
import base64
import openpyxl
import logging
import qrcode
from datetime import datetime, date
from flask import Blueprint, render_template, session, request, jsonify, send_file, current_app
from helpers import login_required, role_required, load_logo, blob_get, blob_set, audit_and_verify, current_branch_id
from models.schema import db, Driver, Vehicle, VehicleCustody
from models.database import db_connection
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger("InvoiceApp")
fleet_bp = Blueprint('fleet', __name__)

import time as _time
# Cache the modern dashboard's insights payload briefly so several staff opening
# /fleet_dashboard around the same time don't each pay the full per-branch blob-scan.
_INSIGHTS_CACHE = {}

@fleet_bp.route("/drivers_info")
@login_required
def drivers_info():
    """صفحة معلومات سائقو النقل العام والخاص"""
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("drivers_info.html", google_user=google_user, b64_en=b64_en)

@fleet_bp.route("/fleet_dashboard")
@login_required
def fleet_dashboard():
    # Modern server-rendered dashboard. It reads the same protected insight API
    # used by the analytics page, so credentials/tokens never reach the browser.
    branches = []
    is_admin = session.get("role") == "admin"
    try:
        with db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM erp_branches")
            branches = [{"id": r[0], "name": r[1]} for r in c.fetchall()]
    except Exception as e:
        logger.error(f"Failed to fetch branches: {e}")
    insights = {"fleet": {"drivers": 0, "with_vehicle": 0, "without_vehicle": 0, "vehicles": 0},
                "volume": {"employees": 0, "workshop": 0, "oils": 0, "purchase": 0, "gps_devices": 0},
                "score": {"value": 0, "label": "غير متاح"},
                "documents": {"expired": 0, "d30": 0}, "documents_top": [],
                "generated_at": "—"}
    try:
        cache_key = current_branch_id()
        cached = _INSIGHTS_CACHE.get(cache_key)
        if cached and cached[0] > _time.time():
            insights = cached[1]
        else:
            insight_view = current_app.view_functions.get("api_insights")
            if insight_view:
                response = insight_view()
                payload = response[0] if isinstance(response, tuple) else response
                data = payload.get_json(silent=True) if hasattr(payload, "get_json") else None
                if data and data.get("success"):
                    insights = data["insights"]
                    _INSIGHTS_CACHE[cache_key] = (_time.time() + 30, insights)
    except Exception:
        logger.exception("modern fleet dashboard insights failed")
    return render_template("fleet_dashboard_new.html", google_user=session.get("google_user"), b64_en=load_logo(), branches=branches, is_admin=is_admin, insights=insights)


def _driver_vehicle_assignment_rows(branch_id):
    """Read-only relationship view; never mutates drivers, vehicles, or custody rows."""
    from models.schema import Driver, Vehicle, VehicleCustody
    rows = []
    custodies = (VehicleCustody.query
                 .join(Driver, VehicleCustody.driver_id == Driver.id)
                 .join(Vehicle, VehicleCustody.vehicle_id == Vehicle.id)
                 .filter(Driver.branch_id == branch_id, Vehicle.branch_id == branch_id)
                 .order_by(VehicleCustody.status.asc(), VehicleCustody.received_date.desc())
                 .all())
    for c in custodies:
        d, v = c.driver, c.vehicle
        rows.append({
            "id": c.id,
            "driver_id": d.id,
            "driver_name": d.name or "غير محدد",
            "employee_id": d.employee_id or "",
            "driver_phone": d.phone or "",
            "driver_status": d.status or "",
            "vehicle_id": v.id,
            "plate": v.plate_number or "",
            "vehicle_type": v.v_type or "",
            "model": v.model or "",
            "serial_number": v.serial_number or "",
            "inspection_expiry": v.inspection_expiry.isoformat() if v.inspection_expiry else "",
            "istimara_expiry": v.istimara_expiry.isoformat() if v.istimara_expiry else "",
            "insurance_expiry": v.insurance_expiry.isoformat() if v.insurance_expiry else "",
            "received_date": c.received_date.isoformat() if c.received_date else "",
            "returned_date": c.returned_date.isoformat() if c.returned_date else "",
            "status": c.status or "active",
            "notes": c.notes or "",
        })
    return rows


@fleet_bp.route("/driver-vehicle-assignments")
@login_required
def driver_vehicle_assignments():
    rows = _driver_vehicle_assignment_rows(current_branch_id())
    return render_template("driver_vehicle_assignments.html", rows=rows,
                           google_user=session.get("google_user"), b64_en=load_logo())


@fleet_bp.route("/api/driver-vehicle-assignments", methods=["GET"])
@login_required
def api_driver_vehicle_assignments():
    return jsonify({"success": True, "read_only": True,
                    "items": _driver_vehicle_assignment_rows(current_branch_id())})

@fleet_bp.route("/api/legacy/drivers", methods=["GET"])
@login_required
def get_drivers():
    branch_id = current_branch_id()
    drivers = Driver.query.filter_by(branch_id=branch_id).order_by(Driver.id.desc()).all()
    
    result = []
    for d in drivers:
        # Reconstruct the flat dictionary expected by the frontend
        item = {
            "id": d.id,
            "name": d.name,
            "empid": d.employee_id,
            "iqama": d.iqama_number,
            "phone": d.phone,
            "job": d.job_title,
            "iqama_exp": d.iqama_expiry.strftime('%Y-%m-%d') if d.iqama_expiry else "",
            "license": d.license_expiry.strftime('%Y-%m-%d') if d.license_expiry else "",
            "status": d.status,
            # Fallbacks for empty vehicle
            "plate": "", "car": "", "model": "", "vserial": "", "inspect": "", "notes": ""
        }
        
        # Check if driver has an active vehicle custody
        active_custody = VehicleCustody.query.filter_by(driver_id=d.id, status="active").first()
        if active_custody and active_custody.vehicle:
            v = active_custody.vehicle
            item.update({
                "plate": v.plate_number,
                "car": v.v_type,
                "model": v.model,
                "vserial": v.serial_number,
                "inspect": v.inspection_expiry.strftime('%Y-%m-%d') if v.inspection_expiry else "",
                "notes": active_custody.notes or ""
            })
            
        result.append(item)
        
    return jsonify(result)

@fleet_bp.route("/api/legacy/drivers", methods=["POST"])
@login_required
def add_driver():
    data = request.json or {}
    fields = ['name', 'empid', 'plate', 'car', 'iqama', 'phone', 'drivercard',
              'job', 'empNotes', 'model', 'pallets', 'load', 'vserial', 
              'inspect', 'license', 'opcard', 'notes', 'fuel_card', 'medical_exp', 'contract_exp']
    
    vals = {f: data.get(f, "").strip() for f in fields}
    
    if not vals['name']:
        return jsonify({"error": "Name is required"}), 400
        
    branch_id = current_branch_id()
    
    def parse_date(dstr):
        if not dstr: return None
        try:
            return datetime.strptime(dstr, '%Y-%m-%d').date()
        except:
            return None

    try:
        driver = Driver(
            branch_id=branch_id,
            name=vals['name'],
            employee_id=vals['empid'] or f"EMP-{datetime.now().timestamp()}",
            iqama_number=vals['iqama'] or None,
            phone=vals['phone'],
            job_title=vals['job'],
            iqama_expiry=parse_date(vals.get('iqama_exp')), # Frontend uses iqama_exp sometimes but sends iqama
            license_expiry=parse_date(vals['license']),
            status="متاح"
        )
        db.session.add(driver)
        db.session.flush() # Get driver.id

        if vals['plate']:
            # See if vehicle exists in this branch
            vehicle = Vehicle.query.filter_by(plate_number=vals['plate']).first()
            if not vehicle:
                vehicle = Vehicle(
                    branch_id=branch_id,
                    plate_number=vals['plate'],
                    v_type=vals['car'],
                    model=vals['model'],
                    serial_number=vals['vserial'],
                    inspection_expiry=parse_date(vals['inspect'])
                )
                db.session.add(vehicle)
                db.session.flush()
                
            custody = VehicleCustody(
                driver_id=driver.id,
                vehicle_id=vehicle.id,
                received_date=datetime.now().date(),
                notes=vals['notes']
            )
            db.session.add(custody)

        db.session.commit()
        logger.info("Driver added via SQLAlchemy: %s (id=%s)", vals['name'], driver.id)
        return jsonify({"success": True, "id": driver.id, **vals})
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error("Error adding driver: IntegrityError (duplicate iqama/employee_id)")
        return jsonify({"success": False, "error": "رقم الإقامة أو الرقم الوظيفي مستخدم مسبقاً لسائق آخر."}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding driver: {type(e).__name__}: {e}")
        return jsonify({"success": False, "error": "تعذّر إضافة السائق."}), 500

@fleet_bp.route("/api/legacy/drivers/<int:driver_id>", methods=["PUT"])
@login_required
def update_driver(driver_id):
    data = request.json or {}
    fields = ['name', 'empid', 'plate', 'car', 'iqama', 'phone', 'drivercard',
              'job', 'empNotes', 'model', 'pallets', 'load', 'vserial', 
              'inspect', 'license', 'opcard', 'notes', 'fuel_card', 'medical_exp', 'contract_exp']
              
    vals = {f: data.get(f, "").strip() for f in fields}

    if not vals['name']:
        return jsonify({"error": "Name is required"}), 400

    def parse_date(dstr):
        if not dstr: return None
        try:
            return datetime.strptime(dstr, '%Y-%m-%d').date()
        except:
            return None

    try:
        from flask import session
        query = Driver.query.filter_by(id=driver_id)
        if session.get("role") != "admin":
            query = query.filter_by(branch_id=current_branch_id())
        driver = query.first()
        if not driver:
            return jsonify({"error": "Driver not found"}), 404

        old_name = driver.name
        old_plate = ""
        
        # Get active custody
        active_custody = VehicleCustody.query.filter_by(driver_id=driver_id, status="active").first()
        if active_custody and active_custody.vehicle:
            old_plate = active_custody.vehicle.plate_number

        # Update Driver
        driver.name = vals['name']
        driver.employee_id = vals['empid'] or driver.employee_id
        driver.iqama_number = vals['iqama'] or driver.iqama_number
        driver.phone = vals['phone']
        driver.job_title = vals['job']
        driver.iqama_expiry = parse_date(vals.get('iqama_exp')) or driver.iqama_expiry
        driver.license_expiry = parse_date(vals['license']) or driver.license_expiry

        # Handle Vehicle Update
        if vals['plate']:
            vehicle = Vehicle.query.filter_by(plate_number=vals['plate']).first()
            if not vehicle:
                # Create new vehicle if plate changed to a non-existent one
                vehicle = Vehicle(
                    branch_id=current_branch_id(),
                    plate_number=vals['plate'],
                    v_type=vals['car'],
                    model=vals['model'],
                    serial_number=vals['vserial'],
                    inspection_expiry=parse_date(vals['inspect'])
                )
                db.session.add(vehicle)
                db.session.flush()
            else:
                # Update existing vehicle fields
                vehicle.v_type = vals['car']
                vehicle.model = vals['model']
                vehicle.serial_number = vals['vserial']
                if vals['inspect']:
                    vehicle.inspection_expiry = parse_date(vals['inspect'])
            
            # Manage Custody
            if not active_custody or active_custody.vehicle_id != vehicle.id:
                if active_custody:
                    active_custody.status = "returned"
                    active_custody.returned_date = datetime.now().date()
                
                new_custody = VehicleCustody(
                    driver_id=driver.id,
                    vehicle_id=vehicle.id,
                    received_date=datetime.now().date(),
                    notes=vals['notes']
                )
                db.session.add(new_custody)
            else:
                active_custody.notes = vals['notes']
        elif active_custody:
            # Plate was cleared, return custody
            active_custody.status = "returned"
            active_custody.returned_date = datetime.now().date()

        db.session.commit()

        # Legacy sync (keep for tabs not yet rewritten)
        if old_name != vals['name'] or old_plate != vals['plate']:
            try:
                # Lives in app.py and was never imported here, so this raised NameError on every
                # rename — swallowed by the except below, so the UI said "updated" while the
                # old name stayed in the schedule, washing and every other tab.
                from app import _sync_all_tabs_from_drivers
                _sync_all_tabs_from_drivers(
                    old_name=old_name, old_plate=old_plate,
                    new_name=vals['name'], new_plate=vals['plate'], new_car=vals['car']
                )
            except Exception as e:
                logger.error(f"Legacy sync failed: {e}")

        logger.info("Driver updated via SQLAlchemy: id=%s name=%s plate=%s", driver_id, vals['name'], vals['plate'])
        return jsonify({"success": True, "id": driver_id, **vals})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating driver: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@fleet_bp.route("/api/fleet_data")

@login_required
def api_fleet_data():
    from models.schema import Driver, Vehicle, VehicleCustody
    fleet = []
    try:
        vehicles = Vehicle.query.all()
        for v in vehicles:
            custody = VehicleCustody.query.filter_by(vehicle_id=v.id, status='active').first()
            d = custody.driver if custody and custody.driver else None
            
            driver_name = ""
            if d:
                driver_name = d.name or ""
            else:
                if v.yard_status in ['معطل', 'معطلة', 'صيانة']:
                    driver_name = "معطلة"
                else:
                    driver_name = "اسبير"

            fleet.append({
                "id": d.id if d else f"v_{v.id}",
                "name": driver_name,
                "empid": d.employee_id if d else "",
                "iqama": d.iqama_number if d else "",
                "plate": v.plate_number or "",
                "car": v.v_type or "",
                "phone": d.phone if d else "",
                "drivercard": "",
                "job": d.job_title if d else "",
                "empNotes": "",
                "model": v.model or "",
                "pallets": "",
                "load": "",
                "vserial": v.serial_number or "",
                "inspect": "",
                "license": "",
                "opcard": "",
                "notes": v.yard_condition or ""
            })
            
        drivers = Driver.query.all()
        assigned_driver_ids = [f["id"] for f in fleet if isinstance(f["id"], int)]
        for d in drivers:
            if d.id not in assigned_driver_ids:
                fleet.append({
                    "id": d.id,
                    "name": d.name or "",
                    "empid": d.employee_id or "",
                    "iqama": d.iqama_number or "",
                    "plate": "",
                    "car": "",
                    "phone": d.phone or "",
                    "drivercard": "",
                    "job": d.job_title or "",
                    "empNotes": "",
                    "model": "",
                    "pallets": "",
                    "load": "",
                    "vserial": "",
                    "inspect": "",
                    "license": "",
                    "opcard": "",
                    "notes": ""
                })
    except Exception as e:
        # The SQLAlchemy tables this route reads are created by a separate manual
        # migration (migrate_db.py), not by the app's own startup init_db(). On a
        # fresh deploy where that migration hasn't run yet, degrade to an empty
        # fleet list instead of a hard 500 that would take down the whole fleet
        # dashboard page.
        logger.error(f"api_fleet_data error (SQLAlchemy tables may be missing): {e}")
        fleet = []
    response = jsonify(fleet)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response
import io
import qrcode
from flask import send_file, url_for

@fleet_bp.route("/api/vehicles/<int:vehicle_id>/qr")
@login_required
def vehicle_qr(vehicle_id):
    branch_id = current_branch_id()
    vehicle = Vehicle.query.filter_by(id=vehicle_id, branch_id=branch_id).first()
    
    if not vehicle:
        return "Vehicle not found", 404
        
    # Generate URL for the vehicle's public/semi-public mobile status page
    # Since we are using an absolute URL, we need to ensure SERVER_NAME is set, or we can build it manually.
    # For now, we will construct the relative URL and use request.host_url
    url = f"{request.host_url}v/{vehicle.id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return send_file(buf, mimetype="image/png")
    
@fleet_bp.route("/v/<int:vehicle_id>")
def vehicle_public_status(vehicle_id):
    # QR / yard vehicle status page — operational fields only (no costs).
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    from models.schema import VehicleCustody
    active_custody = VehicleCustody.query.filter_by(vehicle_id=vehicle.id, status="active").first()
    driver_name = "غير مخصصة"
    driver_phone = ""
    if active_custody and getattr(active_custody, "driver", None):
        driver_name = active_custody.driver.name or "غير مخصصة"
        driver_phone = getattr(active_custody.driver, "phone", None) or ""

    docs_missing = not any([
        vehicle.istimara_expiry,
        vehicle.insurance_expiry,
        vehicle.inspection_expiry,
    ])

    b64_en = load_logo()
    return render_template(
        "vehicle_mobile_status.html",
        vehicle=vehicle,
        driver_name=driver_name,
        driver_phone=driver_phone,
        docs_missing=docs_missing,
        b64_en=b64_en,
    )

@fleet_bp.route("/api/drivers_info_data")
@login_required
def api_drivers_info_data():
    try:
        from models.schema import Driver, Vehicle, VehicleCustody
        branch_id = current_branch_id()
        drivers = Driver.query.filter_by(branch_id=branch_id).all()
        vehicles = {v.id: v for v in Vehicle.query.filter_by(branch_id=branch_id).all()}
        custodies = VehicleCustody.query.filter_by(status='active').all()
        
        driver_custody = {c.driver_id: c for c in custodies}
        
        data = []
        for d in drivers:
            c = driver_custody.get(d.id)
            v = vehicles.get(c.vehicle_id) if c else None
            
            data.append({
                "id": d.id,
                "name": d.name or "",
                "iqama": d.iqama_number or "",
                "phone": d.phone or "",
                "job": d.job_title or "",
                "status": d.status or "نشط",
                "transport_type": "عام" if "عام" in (d.job_title or "") else ("خاص" if "خاص" in (d.job_title or "") else "غير محدد"),
                "has_vehicle": v is not None,
                "plate": v.plate_number if v else "",
                "car": v.v_type if v else "",
                "model": v.model if v else "",
                "vserial": v.serial_number if v else "",
                "notes": getattr(d, 'empNotes', "") or ""
            })
            
        return jsonify(data)
    except Exception as e:
        import traceback
        logger.error(f"Error in api_drivers_info_data: {traceback.format_exc()}")
        return jsonify({"error": f"Error: {str(e)}"}), 500

@fleet_bp.route("/api/vehicle_search")
@login_required
def api_vehicle_search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    from models.schema import Vehicle
    branch_id = current_branch_id()
    # Search by plate
    vs = Vehicle.query.filter(Vehicle.plate_number.ilike(f"%{query}%"), Vehicle.branch_id == branch_id).limit(10).all()
    return jsonify([{
        "id": v.id,
        "plate": v.plate_number,
        "car": v.v_type,
        "model": v.model,
        "vserial": v.serial_number
    } for v in vs])

@fleet_bp.route("/api/drivers_info_save", methods=["POST"])
@login_required
def api_drivers_info_save():
    from models.schema import Driver, Vehicle, VehicleCustody
    import uuid
    try:
        data = request.json
        driver_id = data.get('id')
        name = data.get('name', '').strip()
        iqama = data.get('iqama', '').strip()
        phone = data.get('phone', '').strip()
        job = data.get('job', '').strip()
        status = data.get('status', 'نشط')
        plate = data.get('plate', '').strip()
        car = data.get('car', '').strip()
        model = data.get('model', '').strip()
        reason = data.get('reason', '').strip()
        branch_id = current_branch_id()
        
        if not name:
            return jsonify({"success": False, "error": "اسم السائق مطلوب"})
            
        if driver_id:
            from flask import session
            query = Driver.query.filter_by(id=driver_id)
            if session.get("role") != "admin":
                query = query.filter_by(branch_id=branch_id)
            driver = query.first()
            if not driver:
                return jsonify({"success": False, "error": "السائق غير موجود"})
        else:
            emp_id = iqama if iqama else f'EXT-{str(uuid.uuid4())[:8]}'
            driver = Driver(branch_id=branch_id, employee_id=emp_id)
            db.session.add(driver)
            
        driver.name = name
        driver.iqama_number = iqama
        driver.phone = phone
        driver.job_title = job
        driver.status = status
        
        db.session.flush()

        from datetime import date
        today = date.today()

        def close_active(query):
            """Close historical custody rows without deleting their relationship."""
            active_rows = query.filter_by(status='active').all()
            for custody in active_rows:
                custody.status = 'returned'
                custody.returned_date = today
                custody.notes = ((custody.notes or '') +
                                 (f"\nسبب تغيير الربط: {reason}" if reason else '')).strip()

        if plate:
            vehicle = Vehicle.query.filter_by(plate_number=plate, branch_id=branch_id).first()
            if not vehicle:
                vehicle = Vehicle(plate_number=plate, v_type=car, model=model, branch_id=branch_id)
                db.session.add(vehicle)
                db.session.flush()
            else:
                if car and not vehicle.v_type: vehicle.v_type = car
                if model and not vehicle.model: vehicle.model = model
                
            # Update custody
            existing_custody = VehicleCustody.query.filter_by(driver_id=driver.id, vehicle_id=vehicle.id, status='active').first()
            if not existing_custody:
                current_driver_custody = VehicleCustody.query.filter_by(driver_id=driver.id, status='active').first()
                current_vehicle_custody = VehicleCustody.query.filter_by(vehicle_id=vehicle.id, status='active').first()
                if current_driver_custody or current_vehicle_custody:
                    if len(reason) < 5:
                        return jsonify({"success": False, "error": "سبب التغيير مطلوب (5 أحرف على الأقل)"}), 400
                close_active(VehicleCustody.query.filter_by(driver_id=driver.id))
                close_active(VehicleCustody.query.filter_by(vehicle_id=vehicle.id))
                new_custody = VehicleCustody(driver_id=driver.id, vehicle_id=vehicle.id, received_date=today,
                                             notes=f"سبب إنشاء/تغيير الربط: {reason}" if reason else None)
                db.session.add(new_custody)
        else:
            # Remove custody if plate is cleared
            if VehicleCustody.query.filter_by(driver_id=driver.id, status='active').first() and len(reason) < 5:
                return jsonify({"success": False, "error": "سبب إنهاء الربط مطلوب (5 أحرف على الأقل)"}), 400
            close_active(VehicleCustody.query.filter_by(driver_id=driver.id))
            
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        logger.exception("Error saving driver info")
        return jsonify({"success": False, "error": str(e)}), 500

@fleet_bp.route("/api/driver_search")
@login_required
def api_driver_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    from models.schema import Driver
    # Search by iqama or name
    drivers = Driver.query.filter(
        Driver.branch_id == current_branch_id(),
        db.or_(Driver.iqama_number.like(f"%{q}%"), Driver.name.like(f"%{q}%"))
    ).limit(5).all()
    
    return jsonify([{
        "id": d.id,
        "name": d.name or "",
        "iqama": d.iqama_number or "",
        "phone": d.phone or "",
        "job": d.job_title or "",
        "status": d.status or "نشط"
    } for d in drivers])

@fleet_bp.route("/api/force_db_fix")
@login_required
def api_force_db_fix():
    if current_branch_id() != 1:
        return jsonify({"error": "Unauthorized."}), 403
    try:
        from models.schema import db
        from sqlalchemy import text
        
        commands = [
            "ALTER TABLE erp_vehicles ADD COLUMN IF NOT EXISTS current_km INTEGER;",
            "ALTER TABLE erp_vehicles ADD COLUMN IF NOT EXISTS odometer INTEGER;",
            "ALTER TABLE erp_vehicles ADD COLUMN IF NOT EXISTS pallets VARCHAR(50);",
            "ALTER TABLE erp_vehicles ADD COLUMN IF NOT EXISTS load_capacity VARCHAR(50);",
            "ALTER TABLE erp_vehicles ADD COLUMN IF NOT EXISTS opcard DATE;",
            "ALTER TABLE erp_vehicles ADD COLUMN IF NOT EXISTS fuel_card VARCHAR(50);",
            "ALTER TABLE erp_vehicles ADD COLUMN IF NOT EXISTS notes TEXT;",
            "ALTER TABLE erp_drivers ADD COLUMN IF NOT EXISTS \"empNotes\" TEXT;"
        ]
        
        results = []
        for cmd in commands:
            try:
                db.session.execute(text(cmd))
                results.append(f"SUCCESS: {cmd}")
            except Exception as cmd_err:
                db.session.rollback()
                results.append(f"SKIPPED/ERROR (might already exist or sqlite syntax difference): {str(cmd_err)}")
        
        db.session.commit()
        return jsonify({"success": True, "results": results})
    except Exception as e:
        logger.exception("force_db_fix failed")
        return jsonify({"error": "تعذر إكمال إصلاح قاعدة البيانات"}), 500

@fleet_bp.route("/api/sync_live_numbers_data")
@login_required
def api_sync_live_numbers_data():
    try:
        from models.schema import db, Driver, Vehicle, VehicleCustody
        import json
        import os
        from datetime import date
        
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'extracted_numbers_data.json')
        if not os.path.exists(json_path):
            return jsonify({"error": "Data file not found on server."}), 404
            
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        vehicles_updated = 0
        vehicles_added = 0
        drivers_updated = 0
        drivers_added = 0
        custody_linked = 0
        
        branch_id = 1
        
        all_vehicles = {v.plate_number.replace(" ", ""): v for v in Vehicle.query.all()}
        all_drivers_iqama = {d.iqama_number: d for d in Driver.query.all() if d.iqama_number}
        all_drivers_name = {d.name.strip().lower(): d for d in Driver.query.all() if d.name}
        
        for item in data:
            plate = item.get("plate")
            if not plate: continue
            
            brand = item.get("brand") or ""
            model_type = item.get("model_type") or ""
            model_year = item.get("model_year")
            serial_num = item.get("serial_num")
            vehicle_condition = item.get("vehicle_condition")
            reg_type = item.get("registration_type") or ""
            
            driver_name = item.get("driver_name")
            driver_iqama = item.get("driver_iqama")
            job_title = item.get("job_title")
            raw_phone = item.get("phone")
            
            phone = None
            if raw_phone and raw_phone.lower() != 'none':
                phone = raw_phone if raw_phone.startswith('0') else '0' + raw_phone
                
            v_type = f"{brand} {model_type}".strip()
            
            # Determine transport type from registration_type or job_title
            transport_type = ""
            if "عام" in reg_type:
                transport_type = "سائق نقل عام"
            elif "خاص" in reg_type:
                transport_type = "سائق نقل خاص"
            elif job_title and "عام" in job_title:
                transport_type = "سائق نقل عام"
            elif job_title and "خاص" in job_title:
                transport_type = "سائق نقل خاص"
            
            normalized_plate = plate.replace(" ", "")
            vehicle = all_vehicles.get(normalized_plate)
            
            if vehicle:
                vehicle.plate_number = plate
                if model_year: vehicle.model = model_year
                if v_type: vehicle.v_type = v_type
                if serial_num: vehicle.serial_number = serial_num
                if vehicle_condition: vehicle.yard_condition = vehicle_condition
                vehicles_updated += 1
            else:
                vehicle = Vehicle()
                vehicle.branch_id = branch_id
                vehicle.plate_number = plate
                vehicle.model = model_year
                vehicle.v_type = v_type
                vehicle.serial_number = serial_num
                vehicle.yard_condition = vehicle_condition
                db.session.add(vehicle)
                db.session.flush()
                all_vehicles[normalized_plate] = vehicle
                vehicles_added += 1
                
            driver = None
            if driver_iqama or driver_name:
                if driver_iqama and driver_iqama in all_drivers_iqama:
                    driver = all_drivers_iqama[driver_iqama]
                elif driver_name and driver_name.lower() in all_drivers_name:
                    driver = all_drivers_name[driver_name.lower()]
                    
                if driver:
                    if driver_name: driver.name = driver_name
                    if driver_iqama: driver.iqama_number = driver_iqama
                    if transport_type: driver.job_title = transport_type
                    elif job_title: driver.job_title = job_title
                    if phone: driver.phone = phone
                    drivers_updated += 1
                else:
                    import uuid
                    driver = Driver()
                    driver.branch_id = branch_id
                    driver.employee_id = f"EXT-{uuid.uuid4().hex[:8].upper()}"
                    driver.name = driver_name
                    driver.iqama_number = driver_iqama
                    driver.job_title = transport_type or job_title or ""
                    driver.phone = phone
                    driver.status = 'نشط'
                    db.session.add(driver)
                    db.session.flush()
                    if driver_iqama:
                        all_drivers_iqama[driver_iqama] = driver
                    if driver_name:
                        all_drivers_name[driver_name.lower()] = driver
                    drivers_added += 1
                    
            if driver and vehicle:
                existing_custodies = VehicleCustody.query.filter_by(vehicle_id=vehicle.id, status='active').all()
                needs_new = True
                for c in existing_custodies:
                    if c.driver_id == driver.id:
                        needs_new = False
                    else:
                        c.status = 'returned'
                        c.returned_date = date.today()
                        
                driver_custodies = VehicleCustody.query.filter_by(driver_id=driver.id, status='active').all()
                for c in driver_custodies:
                    if c.vehicle_id != vehicle.id:
                        c.status = 'returned'
                        c.returned_date = date.today()
                        
                if needs_new:
                    new_custody = VehicleCustody()
                    new_custody.driver_id = driver.id
                    new_custody.vehicle_id = vehicle.id
                    new_custody.received_date = date.today()
                    new_custody.status = 'active'
                    db.session.add(new_custody)
                    custody_linked += 1

        db.session.commit()
        return jsonify({
            "success": True,
            "vehicles_added": vehicles_added,
            "vehicles_updated": vehicles_updated,
            "drivers_added": drivers_added,
            "drivers_updated": drivers_updated,
            "custody_linked": custody_linked
        })
    except Exception as e:
        import traceback
        logger.error(f"Sync error: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500

@fleet_bp.route("/master_editor")
@login_required
@role_required("admin")
def master_editor():
    return render_template("master_editor.html", title="التعديل الشامل للبيانات")

@fleet_bp.route("/api/master_data")
@login_required
@role_required("admin")
def api_master_data():
    try:
        from models.schema import Driver, Vehicle, VehicleCustody
        branch_id = current_branch_id()
        drivers = Driver.query.filter_by(branch_id=branch_id).all()
        vehicles = {v.id: v for v in Vehicle.query.filter_by(branch_id=branch_id).all()}
        custodies = VehicleCustody.query.filter_by(status='active').all()
        
        driver_custody = {c.driver_id: c for c in custodies}
        
        data = []
        idx = 1
        for d in drivers:
            c = driver_custody.get(d.id)
            v = vehicles.get(c.vehicle_id) if c else None
            
            data.append({
                "row_num": idx,
                "id": d.id,
                "employee_id": d.employee_id or "",
                "name": d.name or "",
                "iqama_number": d.iqama_number or "",
                "birth_date": str(d.birth_date) if getattr(d, 'birth_date', None) else "",
                "job_title": d.job_title or "",
                "phone": d.phone or "",
                "status": d.status or "متاح",
                "empNotes": d.empNotes or "",
                # Vehicle fields
                "plate_number": v.plate_number if v else "",
                "model": v.model if v else "",
                "v_type": v.v_type if v else "",
                "load_capacity": v.load_capacity if v else "",
                "serial_number": v.serial_number if v else "",
                "inspection_expiry": str(v.inspection_expiry) if v and v.inspection_expiry else "",
                "istimara_expiry": str(v.istimara_expiry) if v and v.istimara_expiry else "",
                "notes": v.notes if v else "",
            })
            idx += 1
            
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error loading master data: {e}")
        return jsonify({"error": str(e)}), 500

@fleet_bp.route("/api/master_data/update", methods=["POST"])
@login_required
def api_master_data_update():
    try:
        from models.schema import db, Driver, Vehicle, VehicleCustody
        data = request.json
        driver_id = data.get("id")
        field = data.get("field")
        value = data.get("value")
        
        if not driver_id or not field:
            return jsonify({"success": False, "error": "Missing parameters"}), 400
            
        from flask import session
        query = Driver.query.filter_by(id=driver_id)
        if session.get("role") != "admin":
            query = query.filter_by(branch_id=current_branch_id())
        driver = query.first()
        if not driver:
            return jsonify({"success": False, "error": "Driver not found"}), 404
            
        # Determine if field belongs to Driver or Vehicle
        driver_fields = ["employee_id", "name", "iqama_number", "phone", "job_title", "status", "birth_date", "empNotes"]
        vehicle_fields = ["plate_number", "v_type", "model", "serial_number", "current_km",
                          "yard_condition", "load_capacity", "istimara_expiry", "inspection_expiry", "notes"]
        
        if field in driver_fields:
            setattr(driver, field, value)
        elif field in vehicle_fields:
            # Find active vehicle
            custody = VehicleCustody.query.filter_by(driver_id=driver.id, status='active').first()
            if custody and custody.vehicle_id:
                vehicle = Vehicle.query.get(custody.vehicle_id)
                if vehicle:
                    setattr(vehicle, field, value)
            else:
                return jsonify({"success": False, "error": "No active vehicle linked to this driver"}), 400
        else:
            return jsonify({"success": False, "error": "Unknown field"}), 400
            
        db.session.commit()
        
        # Log audit (utils.audit never existed, so this silently never logged anything)
        try:
            from helpers import _audit_add
            _audit_add("تعديل", "محرر البيانات الرئيسي", None, f"Updated {field} for Driver ID {driver_id}")
        except Exception:
            pass
            
        return jsonify({"success": True})
        
    except Exception as e:
        import traceback
        logger.error(f"Error updating master data: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500
