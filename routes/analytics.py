"""
analytics.py - Blueprint for Advanced Analytics, Smart Alerts, and Workshop Linkage
"""

from flask import Blueprint, jsonify, request, session
from helpers import login_required, blob_get, blob_set, current_branch_id, role_required, branch_scope
from services.analytics_service import get_operating_costs_summary, get_fuel_efficiency_report, get_operational_kpis
from services.alert_service import check_document_expirations, check_maintenance_schedules
from models.schema import db, Vehicle, WorkshopRecord, SparePart, WorkshopPartUsage
from datetime import datetime, date


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

@analytics_bp.route("/api/alerts/manage", methods=["GET", "POST"])
@login_required
@role_required("admin")
def api_manage_alerts():
    """Admin alert inbox: update the source expiry date or close an action."""
    from app import _global_blob_get, _global_blob_set, _audit_add
    from models.schema import Driver, Document

    def _settings():
        raw = _global_blob_get("alert_settings")
        return raw if isinstance(raw, dict) else {}

    def _actions():
        raw = _settings().get("managed_actions", {})
        return raw if isinstance(raw, dict) else {}

    def _save_actions(actions):
        cfg = _settings()
        cfg["managed_actions"] = actions
        _global_blob_set("alert_settings", cfg)

    if request.method == "GET":
        branch_id = None if session.get("is_admin") else current_branch_id()
        result = check_document_expirations(branch_id=branch_id)
        actions = _actions()
        alerts = []
        for alert in result.get("alerts", []):
            item = dict(alert)
            action = actions.get(item["alert_key"], {})
            item["action_status"] = action.get("status", "open")
            item["completed_at"] = action.get("completed_at", "")
            item["completed_by"] = action.get("completed_by", "")
            item["action_note"] = action.get("note", "")
            alerts.append(item)
        return jsonify({"success": True, "alerts": alerts, "counts": result.get("counts", {})})

    body = request.get_json(silent=True) or {}
    alert_key = str(body.get("alert_key") or "").strip()
    action_type = body.get("action")
    if not alert_key or action_type not in ("complete", "reopen", "update_date"):
        return jsonify({"success": False, "error": "طلب غير صالح."}), 400

    actions = _actions()
    current = actions.get(alert_key, {}) if isinstance(actions.get(alert_key), dict) else {}
    if action_type == "update_date":
        raw_date = str(body.get("date") or "").strip()
        try:
            new_date = date.fromisoformat(raw_date)
        except ValueError:
            return jsonify({"success": False, "error": "التاريخ غير صالح."}), 400
        source = body.get("source")
        field = body.get("field")
        try:
            entity_id = int(body.get("entity_id"))
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "معرّف التنبيه غير صالح."}), 400
        model = {"vehicle": Vehicle, "driver": Driver, "document": Document}.get(source)
        if not model or field not in {"istimara_expiry", "insurance_expiry", "inspection_expiry", "iqama_expiry", "license_expiry", "expiry"}:
            return jsonify({"success": False, "error": "مصدر التنبيه غير صالح."}), 400
        record = model.query.get(entity_id)
        if not record:
            return jsonify({"success": False, "error": "السجل غير موجود."}), 404
        if session.get("is_branch_user") and getattr(record, "branch_id", None) != current_branch_id():
            return jsonify({"success": False, "error": "غير مصرح بهذا السجل."}), 403
        setattr(record, field, new_date)
        db.session.commit()
        current.update({"status": "open", "updated_date": raw_date, "note": str(body.get("note") or "").strip()[:500]})
        actions[alert_key] = current
        _save_actions(actions)
        _audit_add("تعديل تاريخ", "إدارة التنبيهات", str(entity_id), f"{source}.{field} = {raw_date}")
        return jsonify({"success": True, "date": raw_date})

    now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    current.update({"status": "completed" if action_type == "complete" else "open", "completed_at": now if action_type == "complete" else "", "completed_by": session.get("user") or session.get("username") or "admin", "note": str(body.get("note") or "").strip()[:500]})
    actions[alert_key] = current
    _save_actions(actions)
    _audit_add("إنهاء تنبيه" if action_type == "complete" else "إعادة فتح تنبيه", "إدارة التنبيهات", alert_key, current.get("note") or "")
    return jsonify({"success": True, "status": current["status"]})


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
            vq = Vehicle.query.filter_by(plate_number=plate_number)
            if session.get('role') != 'admin':
                vq = vq.filter(branch_scope(Vehicle.branch_id))
            v = vq.first()
            if v: vehicle_id = v.id

        if vehicle_id:
            vq = Vehicle.query.filter_by(id=vehicle_id)
            if session.get('role') != 'admin':
                vq = vq.filter(branch_scope(Vehicle.branch_id))
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
                    pq = pq.filter(branch_scope(SparePart.branch_id))
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
        
        branch_filter = None if session.get('role') == 'admin' else current_branch_id()
        def scoped_count(model):
            query = model.query
            if branch_filter is not None and hasattr(model, 'branch_id'):
                query = query.filter(branch_scope(model.branch_id, branch_filter))
            return query.count()

        db_drivers = scoped_count(Driver)
        db_vehicles = scoped_count(Vehicle)
        ws_records = scoped_count(WorkshopRecord)
        spare_parts = scoped_count(SparePart)
        tires = scoped_count(TireRecord)
        batteries = scoped_count(BatteryRecord)
        fuel_recs = scoped_count(FuelRecord)
        docs = scoped_count(Document)
        
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
