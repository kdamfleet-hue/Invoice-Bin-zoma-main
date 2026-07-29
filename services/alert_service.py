"""
alert_service.py - Automated Smart Alert System Service
Monitors document/license expirations and odometer-based maintenance service alerts.
"""

from models.schema import db, Vehicle, Driver, Document, FuelRecord, WorkshopRecord
from datetime import datetime, date, timedelta
from sqlalchemy import func

def check_document_expirations(branch_id=None):
    """
    Checks all expiring documents (Vehicles, Drivers, Documents)
    and categorizes alerts by urgency (Expired, Critical <= 15d, Warning <= 30d, Upcoming <= 60d).
    """
    try:
        today = date.today()
        alerts = []

        v_query = Vehicle.query
        d_query = Driver.query
        doc_query = Document.query

        if branch_id:
            v_query = v_query.filter_by(branch_id=branch_id)
            d_query = d_query.filter_by(branch_id=branch_id)
            doc_query = doc_query.filter_by(branch_id=branch_id)

        # 1. Vehicle Documents
        for v in v_query.all():
            _check_expiry(alerts, v.istimara_expiry, today, f"استمارة المركبة ({v.plate_number})", "مركبة", v.id, v.plate_number)
            _check_expiry(alerts, v.insurance_expiry, today, f"تأمين المركبة ({v.plate_number})", "مركبة", v.id, v.plate_number)
            _check_expiry(alerts, v.inspection_expiry, today, f"الفحص الدوري للمركبة ({v.plate_number})", "مركبة", v.id, v.plate_number)

        # 2. Driver Documents
        for d in d_query.all():
            _check_expiry(alerts, d.iqama_expiry, today, f"إقامة السائق ({d.name})", "سائق", d.id, d.name)
            _check_expiry(alerts, d.license_expiry, today, f"رخصة قيادة السائق ({d.name})", "سائق", d.id, d.name)

        # 3. Document table records
        for doc in doc_query.all():
            if doc.expiry:
                entity = doc.entity_ref or f"وثيقة #{doc.id}"
                _check_expiry(alerts, doc.expiry, today, f"{doc.doc_type} ({entity})", "وثيقة", doc.id, entity)

        # Sort by urgency level & days remaining
        priority_map = {'expired': 0, 'critical': 1, 'warning': 2, 'upcoming': 3}
        alerts.sort(key=lambda x: (priority_map.get(x['urgency'], 4), x['days_remaining']))

        counts = {
            'expired': sum(1 for a in alerts if a['urgency'] == 'expired'),
            'critical': sum(1 for a in alerts if a['urgency'] == 'critical'),
            'warning': sum(1 for a in alerts if a['urgency'] == 'warning'),
            'upcoming': sum(1 for a in alerts if a['urgency'] == 'upcoming')
        }

        return {
            'success': True,
            'counts': counts,
            'total_alerts': len(alerts),
            'alerts': alerts
        }
    except Exception as e:
        from app import db
        db.session.rollback()
        return {'success': False, 'error': str(e), 'alerts': []}

def _check_expiry(alerts_list, exp_date, today, title, entity_type, entity_id, entity_name):
    if not exp_date:
        return

    days = (exp_date - today).days

    if days < 0:
        urgency = 'expired'
        status_label = f"منتهية منذ {-days} يوم"
        badge_class = "badge-danger"
    elif days <= 15:
        urgency = 'critical'
        status_label = f"متبقي {days} يوم (حرج)"
        badge_class = "badge-critical"
    elif days <= 30:
        urgency = 'warning'
        status_label = f"متبقي {days} يوم (تحذير)"
        badge_class = "badge-warning"
    elif days <= 60:
        urgency = 'upcoming'
        status_label = f"متبقي {days} يوم (قريباً)"
        badge_class = "badge-info"
    else:
        return

    alerts_list.append({
        'title': title,
        'entity_type': entity_type,
        'entity_id': entity_id,
        'entity_name': entity_name,
        'expiry_date': str(exp_date),
        'days_remaining': days,
        'urgency': urgency,
        'status_label': status_label,
        'badge_class': badge_class
    })

def check_maintenance_schedules(branch_id=None, odo_threshold_km=5000):
    """
    Monitors odometer readings and flags vehicles that require periodic oil/service maintenance.
    """
    try:
        query = db.session.query(
            FuelRecord.vehicle_id,
            func.max(FuelRecord.current_odo).label('latest_odo')
        ).group_by(FuelRecord.vehicle_id)

        if branch_id:
            query = query.filter(FuelRecord.branch_id == branch_id)

        results = query.all()
        vehicle_ids = [r[0] for r in results if r[0]]
        vehicles = {v.id: v for v in Vehicle.query.filter(Vehicle.id.in_(vehicle_ids)).all()} if vehicle_ids else {}

        maintenance_alerts = []
        for row in results:
            v_id, latest_odo = row
            if not v_id or not latest_odo: continue
            v = vehicles.get(v_id)
            if not v: continue

            # Get last workshop record exit date/odo if available
            last_ws = WorkshopRecord.query.filter_by(vehicle_id=v_id, status='مغلق').order_by(WorkshopRecord.exit_date.desc()).first()
            
            # Simple periodic maintenance check (every odo_threshold_km)
            km_since_last = latest_odo % odo_threshold_km
            km_until_next = odo_threshold_km - km_since_last

            if km_until_next <= 500:
                maintenance_alerts.append({
                    'vehicle_id': v_id,
                    'plate_number': v.plate_number,
                    'model': v.model or "غير محدد",
                    'current_odo': latest_odo,
                    'km_until_service': km_until_next,
                    'last_service_date': str(last_ws.exit_date) if last_ws and last_ws.exit_date else "غير مسجل",
                    'status': 'صيانة عاجلة مطلوب غيار زيت' if km_until_next <= 100 else 'اقتراب موعد الصيانة'
                })

        maintenance_alerts.sort(key=lambda x: x['km_until_service'])

        return {
            'success': True,
            'alerts_count': len(maintenance_alerts),
            'maintenance_alerts': maintenance_alerts
        }
    except Exception as e:
        from app import db
        db.session.rollback()
        return {'success': False, 'error': str(e), 'maintenance_alerts': []}
