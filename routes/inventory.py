from flask import Blueprint, render_template, request, jsonify, session, current_app, redirect, url_for
from models.schema import TireRecord, BatteryRecord, Vehicle, db
from helpers import role_required, current_branch_id
from datetime import datetime

inventory_bp = Blueprint("inventory_bp", __name__)

@inventory_bp.route("/inventory/tires")
@role_required("admin", "operations", "maintenance")
def tires_index():
    branch_id = current_branch_id()
    tires = TireRecord.query.filter_by(branch_id=branch_id).all()
    vehicles = Vehicle.query.filter_by(branch_id=branch_id).all()
    return render_template("inventory_tires.html", tires=tires, vehicles=vehicles)

@inventory_bp.route("/api/inventory/tires", methods=["POST"])
@role_required("admin", "operations", "maintenance")
def add_tire():
    data = request.json
    try:
        t = TireRecord(
            branch_id=current_branch_id(),
            vehicle_id=data.get("vehicle_id") or None,
            serial_number=data["serial_number"],
            brand=data.get("brand"),
            size=data.get("size"),
            status=data.get("status", "جديد"),
            install_date=datetime.strptime(data["install_date"], "%Y-%m-%d").date() if data.get("install_date") else None,
            notes=data.get("notes")
        )
        db.session.add(t)
        db.session.commit()
        return jsonify({"success": True, "id": t.id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@inventory_bp.route("/api/inventory/tires/<int:tire_id>", methods=["PUT", "DELETE"])
@role_required("admin", "operations", "maintenance")
def manage_tire(tire_id):
    t = TireRecord.query.get_or_404(tire_id)
    if request.method == "DELETE":
        try:
            db.session.delete(t)
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    data = request.json or {}
    try:
        if "vehicle_id" in data:
            t.vehicle_id = data.get("vehicle_id") or None
        if "serial_number" in data:
            t.serial_number = data["serial_number"]
        if "brand" in data:
            t.brand = data["brand"]
        if "size" in data:
            t.size = data["size"]
        if "status" in data:
            t.status = data["status"]
        if "install_date" in data:
            t.install_date = datetime.strptime(data["install_date"], "%Y-%m-%d").date() if data.get("install_date") else None
        if "retread_date" in data:
            t.retread_date = datetime.strptime(data["retread_date"], "%Y-%m-%d").date() if data.get("retread_date") else None
        if "notes" in data:
            t.notes = data["notes"]

        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@inventory_bp.route("/inventory/batteries")
@role_required("admin", "operations", "maintenance")
def batteries_index():
    branch_id = current_branch_id()
    batteries = BatteryRecord.query.filter_by(branch_id=branch_id).all()
    vehicles = Vehicle.query.filter_by(branch_id=branch_id).all()
    return render_template("inventory_batteries.html", batteries=batteries, vehicles=vehicles)

@inventory_bp.route("/api/inventory/batteries", methods=["POST"])
@role_required("admin", "operations", "maintenance")
def add_battery():
    data = request.json
    try:
        b = BatteryRecord(
            branch_id=current_branch_id(),
            vehicle_id=data.get("vehicle_id") or None,
            serial_number=data["serial_number"],
            brand=data.get("brand"),
            capacity=data.get("capacity"),
            status=data.get("status", "نشط"),
            install_date=datetime.strptime(data["install_date"], "%Y-%m-%d").date() if data.get("install_date") else None,
            notes=data.get("notes")
        )
        db.session.add(b)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
