
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session
from helpers import login_required, role_required, load_logo, current_branch_id
from models.schema import db, CustodyItem, Driver

logger = logging.getLogger("InvoiceApp")
custody_bp = Blueprint('custody', __name__)

@custody_bp.route("/custody")
@login_required
@role_required("admin", "operations")
def custody_page():
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("custody.html", google_user=google_user, b64_en=b64_en)

@custody_bp.route("/api/custody", methods=["GET", "POST"])
@login_required
@role_required("admin", "operations")
def api_custody():
    branch_id = current_branch_id()
    
    if request.method == "GET":
        items = CustodyItem.query.filter_by(branch_id=branch_id).all()
        result = []
        for item in items:
            driver = Driver.query.get(item.driver_id)
            driver_name = driver.name if driver else "غير معروف"
            
            result.append({
                "id": item.id,
                "driver_id": item.driver_id,
                "driver_name": driver_name,
                "item_type": item.item_type,
                "item_details": item.item_details,
                "received_date": item.received_date.strftime('%Y-%m-%d') if item.received_date else "",
                "returned_date": item.returned_date.strftime('%Y-%m-%d') if item.returned_date else "",
                "status": item.status,
                "notes": item.notes or ""
            })
        return jsonify({"items": result})
        
    elif request.method == "POST":
        data = request.json
        try:
            received_date = datetime.strptime(data.get("received_date"), '%Y-%m-%d').date()
            
            new_item = CustodyItem(
                branch_id=branch_id,
                driver_id=int(data.get("driver_id")),
                item_type=data.get("item_type"),
                item_details=data.get("item_details", ""),
                received_date=received_date,
                status=data.get("status", "في العهدة"),
                notes=data.get("notes", "")
            )
            db.session.add(new_item)
            
            from helpers import log_audit
            log_audit("إضافة عهدة", "erp_custody_items", None, f"تسليم عهدة ({data.get('item_type')}) للسائق")
            
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            logger.error(f"Error saving custody: {e}")
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

@custody_bp.route("/api/custody/<int:item_id>", methods=["PUT", "DELETE"])
@login_required
@role_required("admin", "operations")
def update_custody(item_id):
    branch_id = current_branch_id()
    item = CustodyItem.query.filter_by(id=item_id, branch_id=branch_id).first()
    
    if not item:
        return jsonify({"error": "Item not found"}), 404
        
    if request.method == "PUT":
        data = request.json
        try:
            if "status" in data:
                item.status = data["status"]
            if "returned_date" in data and data["returned_date"]:
                item.returned_date = datetime.strptime(data["returned_date"], '%Y-%m-%d').date()
            elif "returned_date" in data and not data["returned_date"]:
                item.returned_date = None
            if "notes" in data:
                item.notes = data["notes"]
                
            from helpers import log_audit
            log_audit("تحديث عهدة", "erp_custody_items", item_id, f"تحديث حالة العهدة إلى {item.status}")
                
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
            
    elif request.method == "DELETE":
        try:
            db.session.delete(item)
            
            from helpers import log_audit
            log_audit("حذف عهدة", "erp_custody_items", item_id, "تم حذف سجل العهدة")
            
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
