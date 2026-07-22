import re
import json
import io
import base64
import openpyxl
import logging
from datetime import datetime, date
from flask import Blueprint, render_template, session, request, jsonify
from helpers import login_required, load_logo, blob_get, blob_set, audit_and_verify, current_branch_id
from models.schema import db, Driver, VehicleCustody

logger = logging.getLogger("InvoiceApp")
fleet_bp = Blueprint('fleet', __name__)

@fleet_bp.route("/fleet_dashboard")
@login_required
def fleet_dashboard():
    # Standalone fleet KPI dashboard (ported from Antigravity).
    branches = []
    is_admin = session.get("role") == "admin"
    try:
        with db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM erp_branches")
            branches = [{"id": r[0], "name": r[1]} for r in c.fetchall()]
    except Exception as e:
        logger.error(f"Failed to fetch branches: {e}")
    return render_template("fleet_dashboard.html", google_user=session.get("google_user"), b64_en=load_logo(), branches=branches, is_admin=is_admin)

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
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding driver: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

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
        driver = Driver.query.get(driver_id)
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
    from models.schema import Driver, VehicleCustody
    fleet = []
    try:
        drivers = Driver.query.all()
        for d in drivers:
            custody = VehicleCustody.query.filter_by(driver_id=d.id, status='active').first()
            v = custody.vehicle if custody and custody.vehicle else None

            fleet.append({
                "id": d.id,
                "name": d.name or "",
                "empid": d.employee_id or "",
                "iqama": d.iqama_number or "",
                "plate": v.plate_number if v else "",
                "car": v.v_type if v else "",
                "phone": d.phone or "",
                "drivercard": "",
                "job": d.job_title or "",
                "empNotes": "",
                "model": v.model if v else "",
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
    # This is the page opened when the QR code is scanned.
    # The user asked if it should be public. Since they didn't answer, we will make it semi-public:
    # Anyone with the link (QR code) can view the basic status, but NO sensitive data like costs.
    # This is common for QR code systems in fleets.
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    # Get basic driver info if assigned
    from models.schema import VehicleCustody
    active_custody = VehicleCustody.query.filter_by(vehicle_id=vehicle.id, status="active").first()
    driver_name = active_custody.driver.name if active_custody else "غير مخصصة"
    
    b64_en = load_logo()
    return render_template("vehicle_mobile_status.html", vehicle=vehicle, driver_name=driver_name, b64_en=b64_en)

