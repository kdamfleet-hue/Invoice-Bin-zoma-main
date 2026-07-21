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
        
        # If user is admin, they might want all drivers or a specific branch.
        # If user is not admin, they only see drivers from their branch.
        is_admin = session.get("role") == "admin"
        query = Driver.query
        
        # We can return all drivers and let the frontend filter, since the fleet dashboard expects all drivers for admin.
        if not is_admin:
            query = query.filter_by(branch_id=current_branch_id())
            
        drivers = query.all()
        result = []
        for d in drivers:
            result.append({
                "id": d.id,
                "empid": d.employee_id,
                "name": d.name,
                "iqama": d.iqama_number,
                "phone": d.phone,
                "job": d.job_title,
                "status": d.status,
                "branch_id": d.branch_id
            })
        return jsonify({"success": True, "data": result})
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
