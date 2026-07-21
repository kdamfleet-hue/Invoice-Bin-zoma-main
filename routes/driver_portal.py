from flask import Blueprint, render_template, request, jsonify, session, current_app, redirect, url_for
from models.schema import Driver, PettyCash, Vehicle, VehicleCustody, db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

driver_portal_bp = Blueprint("driver_portal_bp", __name__)

def get_current_driver():
    driver_id = session.get("driver_id")
    if not driver_id:
        return None
    return Driver.query.get(driver_id)

@driver_portal_bp.route("/driver", methods=["GET", "POST"])
def driver_login():
    if request.method == "POST":
        # Simplified login: iqama_number and phone
        iqama = request.form.get("iqama_number", "").strip()
        phone = request.form.get("phone", "").strip()
        
        # input sanitization
        if not iqama or not phone:
            return render_template("driver_login.html", error="الرجاء إدخال رقم الهوية ورقم الجوال")
            
        driver = Driver.query.filter_by(iqama_number=iqama, phone=phone).first()
        if driver:
            session["driver_id"] = driver.id
            return redirect(url_for("driver_portal_bp.driver_dashboard"))
        else:
            return render_template("driver_login.html", error="بيانات الدخول غير صحيحة")
            
    if session.get("driver_id"):
        return redirect(url_for("driver_portal_bp.driver_dashboard"))
        
    # load logo for ui
    import helpers
    b64_en = helpers.load_logo()
    return render_template("driver_login.html", b64_en=b64_en)

@driver_portal_bp.route("/driver/logout")
def driver_logout():
    session.pop("driver_id", None)
    return redirect(url_for("driver_portal_bp.driver_login"))

@driver_portal_bp.route("/driver/dashboard")
def driver_dashboard():
    driver = get_current_driver()
    if not driver:
        return redirect(url_for("driver_portal_bp.driver_login"))
        
    # Get active vehicle
    active_custody = VehicleCustody.query.filter_by(driver_id=driver.id, status="active").first()
    vehicle = active_custody.vehicle if active_custody else None
    
    # Get petty cash history
    expenses = PettyCash.query.filter_by(driver_id=driver.id).order_by(PettyCash.date.desc()).all()
    
    import helpers
    b64_en = helpers.load_logo()
    return render_template("driver_dashboard.html", driver=driver, vehicle=vehicle, expenses=expenses, b64_en=b64_en)

@driver_portal_bp.route("/api/driver/petty_cash", methods=["POST"])
def submit_petty_cash():
    driver = get_current_driver()
    if not driver:
        return jsonify({"success": False, "error": "غير مصرح"}), 401
        
    amount = request.form.get("amount")
    expense_type = request.form.get("expense_type")
    description = request.form.get("description")
    
    if not amount or not expense_type:
        return jsonify({"success": False, "error": "بيانات غير مكتملة"}), 400
        
    try:
        pc = PettyCash(
            branch_id=driver.branch_id,
            driver_id=driver.id,
            amount=float(amount),
            expense_type=expense_type,
            description=description,
            date=datetime.now().date()
        )
        # handle file upload later if needed
        db.session.add(pc)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

