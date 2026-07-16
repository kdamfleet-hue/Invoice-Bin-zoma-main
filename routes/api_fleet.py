from flask import Blueprint, request, jsonify
from app import login_required
from models.schema import db, Driver, Vehicle, VehicleCustody

api_fleet_bp = Blueprint('api_fleet', __name__)

@api_fleet_bp.route("/api/drivers", methods=["GET"])
@login_required
def get_drivers():
    try:
        # Fetch all drivers from SQLAlchemy model
        drivers = Driver.query.all()
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
                # Optionally map to old format keys if frontend expects them
            })
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@api_fleet_bp.route("/api/drivers", methods=["POST"])
@login_required
def add_driver():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        new_driver = Driver(
            branch_id=1, # Default for now
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
        
        db.session.commit()
        return jsonify({"success": True, "message": "تم تحديث بيانات السائق"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

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
