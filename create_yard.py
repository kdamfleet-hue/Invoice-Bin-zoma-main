import os

code = """
import logging
from flask import Blueprint, render_template, request, jsonify, session
from helpers import login_required, role_required, load_logo, current_branch_id
from models.schema import db, Vehicle

logger = logging.getLogger("InvoiceApp")
yard_bp = Blueprint('yard', __name__)

@yard_bp.route("/yard")
@login_required
@role_required("admin", "operations")
def yard_page():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("yard.html", google_user=google_user, b64_en=b64_en)

@yard_bp.route("/api/yard", methods=["GET"])
@login_required
def api_yard():
    branch_id = current_branch_id()
    vehicles = Vehicle.query.filter_by(branch_id=branch_id).all()
    
    result = []
    for v in vehicles:
        result.append({
            "id": v.id,
            "plate": v.plate_number,
            "type": v.v_type,
            "status": v.yard_status or "خارج الساحة",
            "condition": v.yard_condition or "غير محدد"
        })
    return jsonify({"vehicles": result})

@yard_bp.route("/api/yard/<int:vehicle_id>", methods=["PUT"])
@login_required
@role_required("admin", "operations")
def update_yard(vehicle_id):
    branch_id = current_branch_id()
    v = Vehicle.query.filter_by(id=vehicle_id, branch_id=branch_id).first()
    if not v:
        return jsonify({"error": "Vehicle not found"}), 404
        
    data = request.json
    try:
        if "status" in data:
            v.yard_status = data["status"]
        if "condition" in data:
            v.yard_condition = data["condition"]
            
        from helpers import log_audit
        log_audit("تحديث ساحة", "erp_vehicles", vehicle_id, f"تم تحديث موقع المركبة إلى {v.yard_status} ({v.yard_condition})")
        
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
"""

with open("routes/yard.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Created yard.py")
