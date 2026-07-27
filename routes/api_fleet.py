from flask import Blueprint, request, jsonify
from app import login_required
from models.schema import db, Driver, Vehicle, VehicleCustody

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
                custody = VehicleCustody.query.filter_by(driver_id=d.id).first()
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
                "odometer": km_val or ""
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
        
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        # Determine branch_id
        is_admin = session.get("role") == "admin"
        branch_id = current_branch_id()
        if is_admin and data.get("branch_id"):
            branch_id = int(data.get("branch_id"))
            
        new_driver = Driver(
            branch_id=branch_id,
            employee_id=data.get("empid", ""),
            name=data.get("name", ""),
            iqama_number=data.get("iqama", ""),
            phone=data.get("phone", ""),
            job_title=data.get("job", ""),
            status=data.get("status", "نشط")
        )
        db.session.add(new_driver)
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
        
        data = request.json
        driver = Driver.query.get(driver_id)
        if not driver:
            return jsonify({"success": False, "error": "Driver not found"}), 404
            
        driver.employee_id = data.get("empid", driver.employee_id)
        driver.name = data.get("name", driver.name)
        driver.iqama_number = data.get("iqama", driver.iqama_number)
        driver.phone = data.get("phone", driver.phone)
        driver.job_title = data.get("job", driver.job_title)
        driver.status = data.get("status", driver.status)
        
        if session.get("role") == "admin" and "branch_id" in data:
            val = data.get("branch_id")
            driver.branch_id = int(val) if val else None
        
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
