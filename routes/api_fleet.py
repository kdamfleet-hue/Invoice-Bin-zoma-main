import hmac
import os
from flask import Blueprint, request, jsonify
from utils.birth_mapping import load_birth_mapping
from app import login_required
from models.schema import db, Driver, Vehicle, VehicleCustody, Branch, Document

api_fleet_bp = Blueprint('api_fleet', __name__)

@api_fleet_bp.route("/api/drivers", methods=["GET"])
@login_required
def get_drivers():
    try:
        from flask import session
        from app import current_branch_id
        from helpers import blob_get
        
        is_admin = session.get("role") == "admin"

        # Build enrichment lookup from schedule_data, employees, and fuel_data blobs
        blob_lookup = {}
        s_blob = blob_get("schedule_data") or []
        if isinstance(s_blob, dict) and "rows" in s_blob:
            s_blob = s_blob["rows"]
        if isinstance(s_blob, list):
            for row in s_blob:
                if isinstance(row, dict):
                    k1 = str(row.get("empid", "")).strip()
                    k2 = str(row.get("iqama", "")).strip()
                    k3 = str(row.get("name", "")).strip()
                    entry = {
                        "plate": row.get("plate", ""),
                        "car": row.get("vtype", row.get("car", "")),
                        "model": row.get("model", ""),
                        "phone": row.get("phone", ""),
                        "job": row.get("job", ""),
                        "odometer": row.get("odometer", row.get("km", ""))
                    }
                    if k1: blob_lookup[k1] = entry
                    if k2: blob_lookup[k2] = entry
                    if k3: blob_lookup[k3] = entry

        e_blob = blob_get("employees") or []
        if isinstance(e_blob, dict) and "data" in e_blob:
            e_blob = e_blob["data"]
            if isinstance(e_blob, list):
                for item in e_blob:
                    if isinstance(item, dict):
                        k1 = str(item.get("empid", "")).strip()
                        k2 = str(item.get("iqama", "")).strip()
                        k3 = str(item.get("name", "")).strip()
                        entry = {
                            "plate": item.get("plate", ""),
                            "car": item.get("car", item.get("vtype", "")),
                            "model": item.get("model", ""),
                            "phone": item.get("phone", ""),
                            "job": item.get("job", ""),
                            "odometer": item.get("odometer", item.get("current_km", item.get("km", "")))
                        }
                        if k1 and k1 not in blob_lookup: blob_lookup[k1] = entry
                        if k2 and k2 not in blob_lookup: blob_lookup[k2] = entry
                        if k3 and k3 not in blob_lookup: blob_lookup[k3] = entry

        query = Driver.query
        if not is_admin:
            query = query.filter_by(branch_id=current_branch_id())
            
        drivers = query.all()
        result = []
        for d in drivers:
            try:
                custody = (VehicleCustody.query
                           .filter_by(driver_id=d.id, status="active")
                           .order_by(VehicleCustody.id.desc())
                           .first())
                if not custody:
                    # No row marked "active" (older data from before custody status was
                    # tracked correctly) — fall back to the most recent assignment overall.
                    custody = (VehicleCustody.query
                               .filter_by(driver_id=d.id)
                               .order_by(VehicleCustody.id.desc())
                               .first())
                v = custody.vehicle if custody and custody.vehicle else None
            except Exception:
                v = None

            empid_str = str(d.employee_id or "").strip()
            iqama_str = str(d.iqama_number or "").strip()
            name_str = str(d.name or "").strip()
            blob_entry = blob_lookup.get(empid_str) or blob_lookup.get(iqama_str) or blob_lookup.get(name_str) or {}

            plate_val = (v.plate_number if v else "") or blob_entry.get("plate", "")
            car_val = (v.v_type if v else "") or blob_entry.get("car", "")
            model_val = (v.model if v else "") or blob_entry.get("model", "")
            phone_val = d.phone or blob_entry.get("phone", "")
            job_val = d.job_title or blob_entry.get("job", "")
            km_val = (getattr(v, 'current_km', None) or getattr(v, 'odometer', None)) if v else blob_entry.get("odometer", "")

            result.append({
                "id": d.id,
                "empid": d.employee_id or "",
                "name": d.name or "",
                "iqama": d.iqama_number or "",
                "phone": phone_val or "",
                "job": job_val or "",
                "status": d.status,
                "branch_id": d.branch_id,
                "plate": plate_val or "",
                "car": car_val or "",
                "model": model_val or "",
                "odometer": km_val or "",
                "birth_date": load_birth_mapping().get(d.employee_id or "")
            })

        # Fallback if SQL Driver table is empty
        if not result:
            for k, item in blob_lookup.items():
                if isinstance(item, dict) and (item.get("name") or item.get("plate")):
                    result.append({
                        "id": len(result) + 1,
                        "name": item.get("name", ""),
                        "empid": item.get("empid", ""),
                        "plate": item.get("plate", ""),
                        "car": item.get("car", item.get("vtype", "")),
                        "iqama": item.get("iqama", ""),
                        "phone": item.get("phone", ""),
                        "job": item.get("job", ""),
                        "model": item.get("model", ""),
                        "odometer": item.get("odometer", "")
                    })

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_fleet_bp.route("/api/drivers", methods=["POST"])
@login_required
def add_driver():
    try:
        from flask import session
        from app import current_branch_id
        from datetime import datetime

        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # Determine branch_id
        is_admin = session.get("role") == "admin"
        branch_id = current_branch_id()
        if is_admin and data.get("branch_id"):
            branch_id = int(data.get("branch_id"))
            
        def safe_date(d_str):
            if not d_str or str(d_str).strip() == '': return None
            try: return datetime.strptime(str(d_str).strip(), '%Y-%m-%d').date()
            except: return None

        new_driver = Driver()
        new_driver.branch_id = branch_id
        new_driver.employee_id = data.get("empid", "")
        new_driver.name = data.get("name", "")
        new_driver.iqama_number = data.get("iqama", "")
        new_driver.phone = data.get("phone", "")
        new_driver.job_title = data.get("job", "")
        new_driver.status = data.get("status", "نشط")
        new_driver.drivercard = data.get("drivercard", "")
        new_driver.empNotes = data.get("empNotes", "")
        new_driver.medical_exp = safe_date(data.get("medical_exp"))
        new_driver.contract_exp = safe_date(data.get("contract_exp"))
        
        db.session.add(new_driver)
        
        # Vehicle logic
        plate = data.get("plate", "").strip()
        if plate:
            vehicle = Vehicle.query.filter_by(plate_number=plate).first()
            if not vehicle:
                vehicle = Vehicle()
                vehicle.branch_id = branch_id
                vehicle.plate_number = plate
                vehicle.model = data.get("model", "")
                vehicle.v_type = data.get("car", "")
                vehicle.serial_number = data.get("vserial", "")
                vehicle.pallets = data.get("pallets", "")
                vehicle.load_capacity = data.get("load", "")
                vehicle.fuel_card = data.get("fuel_card", "")
                vehicle.notes = data.get("notes", "")
                vehicle.inspection_expiry = safe_date(data.get("inspect"))
                vehicle.istimara_expiry = safe_date(data.get("license"))
                vehicle.insurance_expiry = safe_date(data.get("opcard"))
                
                db.session.add(vehicle)
            
            db.session.flush() # get IDs
            custody = VehicleCustody()
            custody.driver_id = new_driver.id
            custody.vehicle_id = vehicle.id
            custody.received_date = datetime.utcnow().date()
            db.session.add(custody)

        db.session.commit()
        return jsonify({"success": True, "message": "تم إضافة السائق بنجاح", "id": new_driver.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@api_fleet_bp.route("/api/drivers/<int:driver_id>", methods=["PUT"])
@login_required
def update_driver(driver_id):
    try:
        from flask import session
        from datetime import datetime

        data = request.json
        driver = Driver.query.get(driver_id)
        if not driver:
            return jsonify({"success": False, "error": "Driver not found"}), 404
            
        def safe_date(d_str):
            if not d_str or str(d_str).strip() == '': return None
            try: return datetime.strptime(str(d_str).strip(), '%Y-%m-%d').date()
            except: return None

        driver.employee_id = data.get("empid", driver.employee_id)
        driver.name = data.get("name", driver.name)
        driver.iqama_number = data.get("iqama", driver.iqama_number)
        driver.phone = data.get("phone", driver.phone)
        driver.job_title = data.get("job", driver.job_title)
        driver.status = data.get("status", driver.status)
        driver.drivercard = data.get("drivercard", driver.drivercard)
        driver.empNotes = data.get("empNotes", driver.empNotes)
        if "medical_exp" in data: driver.medical_exp = safe_date(data.get("medical_exp"))
        if "contract_exp" in data: driver.contract_exp = safe_date(data.get("contract_exp"))

        if session.get("role") == "admin" and "branch_id" in data:
            val = data.get("branch_id")
            driver.branch_id = int(val) if val else None
            
        # Vehicle logic
        plate = data.get("plate", "").strip()
        if plate:
            vehicle = Vehicle.query.filter_by(plate_number=plate).first()
            if not vehicle:
                vehicle = Vehicle()
                vehicle.branch_id = driver.branch_id
                vehicle.plate_number = plate
                db.session.add(vehicle)
                
            vehicle.model = data.get("model", vehicle.model)
            vehicle.v_type = data.get("car", vehicle.v_type)
            vehicle.serial_number = data.get("vserial", vehicle.serial_number)
            vehicle.pallets = data.get("pallets", vehicle.pallets)
            vehicle.load_capacity = data.get("load", vehicle.load_capacity)
            vehicle.fuel_card = data.get("fuel_card", vehicle.fuel_card)
            vehicle.notes = data.get("notes", vehicle.notes)
            if "inspect" in data: vehicle.inspection_expiry = safe_date(data.get("inspect"))
            if "license" in data: vehicle.istimara_expiry = safe_date(data.get("license"))
            if "opcard" in data: vehicle.insurance_expiry = safe_date(data.get("opcard"))
            
            # Check custody
            db.session.flush()

            # Close any OTHER vehicle this driver currently holds — unconditionally, before
            # deciding whether we're creating a new custody or reactivating an old one for
            # THIS vehicle — so exactly one stays "active" per driver in every case. Doing
            # this only inside the "new custody" branch (as an earlier version of this fix
            # did) missed the case where the driver is reassigned back to a vehicle they'd
            # previously returned: reactivating that old row without also closing whatever
            # they currently hold would leave two custodies "active" at once.
            other_active = VehicleCustody.query.filter(
                VehicleCustody.driver_id == driver.id,
                VehicleCustody.vehicle_id != vehicle.id,
                VehicleCustody.status == "active"
            ).all()
            for oc in other_active:
                oc.status = "returned"
                oc.returned_date = datetime.utcnow().date()

            custody = VehicleCustody.query.filter_by(driver_id=driver.id, vehicle_id=vehicle.id).first()
            if not custody:
                custody = VehicleCustody()
                custody.driver_id = driver.id
                custody.vehicle_id = vehicle.id
                custody.received_date = datetime.utcnow().date()
                custody.status = "active"
                db.session.add(custody)
            elif custody.status != "active":
                # Re-assigning a vehicle they'd previously returned — reactivate it.
                custody.status = "active"
                custody.returned_date = None

        db.session.commit()
        return jsonify({"success": True, "message": "تم تحديث بيانات السائق"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@api_fleet_bp.route('/api/update_driver_branch', methods=['POST'])
@login_required
def update_driver_branch():
    from flask import session
    if session.get('role') != 'admin':
        return jsonify({"success": False, "error": "غير مصرح لك"}), 403
    data = request.json
    driver_id = data.get('id')
    branch_id = data.get('branch_id')
    if driver_id and branch_id is not None:
        try:
            driver = Driver.query.get(driver_id)
            if driver:
                driver.branch_id = int(branch_id)
                db.session.commit()
                return jsonify({"success": True})
            return jsonify({"success": False, "error": "السائق غير موجود"}), 404
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
    return jsonify({"success": False, "error": "بيانات غير صالحة"}), 400

@api_fleet_bp.route("/api/drivers/<int:driver_id>", methods=["DELETE"])
@login_required
def delete_driver(driver_id):
    try:
        driver = Driver.query.get(driver_id)
        if not driver:
            return jsonify({"success": False, "error": "Driver not found"}), 404
            
        db.session.delete(driver)
        db.session.commit()
        return jsonify({"success": True, "message": "تم حذف السائق بنجاح"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@api_fleet_bp.route("/api/vehicle_profile/<path:plate>", methods=["GET"])
@login_required
def vehicle_profile(plate):
    """Returns complete 360 profile for a vehicle: current specs, workshop history, fuel logs, and driver."""
    try:
        from helpers import blob_get
        plate_str = str(plate).strip()
        
        # 1. Driver/Fleet lookup
        employees_blob = blob_get("employees") or {}
        emp_list = employees_blob.get("data", []) if isinstance(employees_blob, dict) else []
        matched_emp = next((e for e in emp_list if isinstance(e, dict) and str(e.get("plate", "")).strip() == plate_str), {})

        sch_blob = blob_get("schedule_data") or {}
        sch_list = sch_blob.get("rows", []) if isinstance(sch_blob, dict) else []
        matched_sch = next((s for s in sch_list if isinstance(s, dict) and str(s.get("plate", "")).strip() == plate_str), {})

        # 2. Fuel records history
        fuel_blob = blob_get("fuel_data") or []
        if isinstance(fuel_blob, dict): fuel_blob = fuel_blob.get("data", [])
        matched_fuel = [f for f in fuel_blob if isinstance(f, dict) and str(f.get("plate", "")).strip() == plate_str]

        # 3. Workshop records history
        workshop_blob = blob_get("workshop_data") or {}
        matched_workshop = []
        if isinstance(workshop_blob, dict) and str(workshop_blob.get("plate", "")).strip() == plate_str:
            matched_workshop.append(workshop_blob)

        # Build response
        res_data = {
            "plate": plate_str,
            "car": matched_emp.get("car") or matched_sch.get("vtype") or matched_emp.get("vtype", "غير محدد"),
            "model": matched_emp.get("model") or matched_sch.get("model", "-"),
            "driver": matched_emp.get("name") or matched_sch.get("name", "غير محدد"),
            "phone": matched_emp.get("phone") or matched_sch.get("phone", "-"),
            "odometer": matched_emp.get("odometer") or matched_sch.get("odometer") or matched_emp.get("km", "0"),
            "fuel_logs_count": len(matched_fuel),
            "fuel_history": matched_fuel[-5:], # last 5 fuel records
            "workshop_records": matched_workshop
        }
        return jsonify({"success": True, "data": res_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_fleet_bp.route("/api/signal-room/summary", methods=["GET"])
def signal_room_summary():
    """Read-only, aggregate data endpoint for the external Signal Room dashboard."""
    configured_key = (os.environ.get("SIGNAL_ROOM_SERVICE_KEY") or "").strip()
    provided_key = (request.headers.get("X-Signal-Room-Key") or "").strip()
    if not configured_key or not provided_key or not hmac.compare_digest(provided_key, configured_key):
        return jsonify({"success": False, "error": "unauthorized"}), 401
    try:
        return jsonify({
            "success": True,
            "data": {
                "branches": Branch.query.count(),
                "drivers": Driver.query.count(),
                "vehicles": Vehicle.query.count(),
                "documents": Document.query.count(),
            },
        })
    except Exception:
        return jsonify({"success": False, "error": "summary_unavailable"}), 503
