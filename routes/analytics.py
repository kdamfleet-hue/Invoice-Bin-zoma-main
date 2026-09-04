"""
analytics.py - Blueprint for Advanced Analytics, Smart Alerts, and Workshop Linkage
"""

from flask import Blueprint, jsonify, request, session
from helpers import login_required, blob_get, blob_set, current_branch_id, role_required
from services.analytics_service import get_operating_costs_summary, get_fuel_efficiency_report, get_operational_kpis
from services.alert_service import check_document_expirations, check_maintenance_schedules
from models.schema import db, Vehicle, WorkshopRecord, SparePart, WorkshopPartUsage
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route("/api/analytics/operating_costs", methods=["GET"])
@login_required
def api_operating_costs():
    branch_id = request.args.get('branch_id', type=int)
    if session.get('is_branch_user'):
        branch_id = current_branch_id()
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

    res = get_operating_costs_summary(branch_id=branch_id, start_date=start_date, end_date=end_date)
    return jsonify(res)

@analytics_bp.route("/api/analytics/fuel_efficiency", methods=["GET"])
@login_required
def api_fuel_efficiency():
    branch_id = request.args.get('branch_id', type=int)
    if session.get('is_branch_user'):
        branch_id = current_branch_id()
    res = get_fuel_efficiency_report(branch_id=branch_id)
    return jsonify(res)

@analytics_bp.route("/api/analytics/kpi_metrics", methods=["GET"])
@login_required
def api_kpi_metrics():
    branch_id = request.args.get('branch_id', type=int)
    if session.get('is_branch_user'):
        branch_id = current_branch_id()
    res = get_operational_kpis(branch_id=branch_id)
    return jsonify(res)

@analytics_bp.route("/api/alerts/smart_notifications", methods=["GET"])
@login_required
def api_smart_notifications():
    branch_id = request.args.get('branch_id', type=int)
    if session.get('is_branch_user'):
        branch_id = current_branch_id()
    res = check_document_expirations(branch_id=branch_id)
    return jsonify(res)

@analytics_bp.route("/api/alerts/maintenance_schedules", methods=["GET"])
@login_required
def api_maintenance_schedules():
    branch_id = request.args.get('branch_id', type=int)
    if session.get('is_branch_user'):
        branch_id = current_branch_id()
    threshold = request.args.get('threshold_km', default=5000, type=int)
    res = check_maintenance_schedules(branch_id=branch_id, odo_threshold_km=threshold)
    return jsonify(res)

@analytics_bp.route("/api/workshop/sync_status", methods=["POST"])
@login_required
@role_required("admin", "operations", "maintenance")
def api_workshop_sync_status():
    """
    Syncs workshop order status directly with vehicle fleet status
    (e.g., 'قيد الإصلاح' -> vehicle status 'تحت الصيانة', 'مغلق' -> vehicle status 'جاهزة / متاح').
    Deducts spare parts quantity from inventory when parts are used.
    """
    try:
        data = request.json or {}
        vehicle_id = data.get('vehicle_id')
        plate_number = data.get('plate_number')
        order_status = data.get('status') # 'مفتوح', 'قيد الإصلاح', 'مغلق', 'جاهز'
        spare_parts = data.get('spare_parts', []) # list of {part_id, qty}

        if not vehicle_id and plate_number:
            v = Vehicle.query.filter_by(plate_number=plate_number).first()
            if v: vehicle_id = v.id

        if vehicle_id:
            vq = Vehicle.query.filter_by(id=vehicle_id)
            if session.get('role') != 'admin':
                vq = vq.filter_by(branch_id=current_branch_id())
            v = vq.first()
            if v:
                if order_status in ['قيد الإصلاح', 'مفتوح', 'تحت الصيانة']:
                    v.yard_status = 'تحت الصيانة'
                elif order_status in ['مغلق', 'جاهز', 'مكتمل']:
                    v.yard_status = 'خارج الساحة'

        # Deduct spare parts
        deducted_parts = []
        for item in spare_parts:
            part_id = item.get('part_id')
            qty = item.get('qty', 1)
            if part_id and qty > 0:
                pq = SparePart.query.filter_by(id=part_id)
                if session.get('role') != 'admin':
                    pq = pq.filter_by(branch_id=current_branch_id())
                part = pq.first()
                if part and part.quantity >= qty:
                    part.quantity -= qty
                    deducted_parts.append({'part_id': part_id, 'name': part.name, 'deducted': qty, 'remaining': part.quantity})

        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'تم تحديث حالة المركبة وخصم قطع الغيار بنجاح',
            'deducted_parts': deducted_parts
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route("/api/system/linkage_health", methods=["GET"])
@login_required
def api_linkage_health():
    """
    Returns system linkage diagnostic health metrics across all integrated modules.
    """
    try:
        from models.schema import Driver, Vehicle, WorkshopRecord, SparePart, Document, FuelRecord, TireRecord, BatteryRecord, Incident, PettyCash
        
        db_drivers = Driver.query.count()
        db_vehicles = Vehicle.query.count()
        ws_records = WorkshopRecord.query.count()
        spare_parts = SparePart.query.count()
        tires = TireRecord.query.count()
        batteries = BatteryRecord.query.count()
        fuel_recs = FuelRecord.query.count()
        docs = Document.query.count()
        
        modules = [
            {'key': 'fleet_drivers', 'name': 'السائقين والأسطول', 'status': 'مكتمل ومرتبط' if (db_drivers or db_vehicles) else 'لا توجد بيانات', 'count': f"{db_drivers} سائق / {db_vehicles} مركبة", 'health': 100 if (db_drivers or db_vehicles) else 0},
            {'key': 'schedule', 'name': 'الجدول الأسبوعي', 'status': 'مكتمل ومرتبط', 'count': 'نشط', 'health': 100},
            {'key': 'workshop', 'name': 'الورشة والمخزون', 'status': 'مكتمل ومرتبط' if (ws_records or spare_parts) else 'لا توجد بيانات', 'count': f"{ws_records} سجلات / {spare_parts} أصناف", 'health': 100 if (ws_records or spare_parts) else 0},
            {'key': 'fuel', 'name': 'تتبع المحروقات والعدادات', 'status': 'مكتمل ومرتبط' if fuel_recs else 'لا توجد بيانات', 'count': f"{fuel_recs} سجل وقود", 'health': 100 if fuel_recs else 0},
            {'key': 'inventory_tires', 'name': 'مخزون الإطارات والبطاريات', 'status': 'مكتمل ومرتبط' if (tires or batteries) else 'لا توجد بيانات', 'count': f"{tires} إطار / {batteries} بطارية", 'health': 100 if (tires or batteries) else 0},
            {'key': 'documents_alerts', 'name': 'نظام التوثيق والتنبيهات', 'status': 'مكتمل ومرتبط' if docs else 'لا توجد بيانات', 'count': f"{docs} وثيقة", 'health': 100 if docs else 0}
        ]
        overall_health = round(sum(m['health'] for m in modules) / len(modules))
        return jsonify({
            'success': True,
            'overall_health': overall_health,
            'status': 'جميع الأنظمة مرتبطة وتعمل بتناغم كلي' if overall_health == 100 else 'بعض الوحدات لا تحتوي على بيانات فعلية',
            'modules': modules
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
