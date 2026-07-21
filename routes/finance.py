from flask import Blueprint, render_template, request, jsonify, session
from models.schema import PettyCash, Driver, db
from helpers import role_required, current_branch_id

finance_bp = Blueprint("finance_bp", __name__)

@finance_bp.route("/finance/petty-cash")
@role_required("admin", "operations", "data_entry")
def petty_cash_index():
    branch_id = current_branch_id()
    expenses = PettyCash.query.filter_by(branch_id=branch_id).order_by(PettyCash.date.desc()).all()
    return render_template("petty_cash.html", expenses=expenses)

@finance_bp.route("/api/finance/petty-cash/<int:id>/status", methods=["POST"])
@role_required("admin", "operations")
def update_petty_cash_status(id):
    data = request.json
    status = data.get("status")
    if status not in ["معتمد", "مرفوض"]:
        return jsonify({"success": False, "error": "حالة غير صالحة"}), 400
        
    pc = PettyCash.query.get(id)
    if not pc:
        return jsonify({"success": False, "error": "غير موجود"}), 404
        
    try:
        pc.status = status
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
