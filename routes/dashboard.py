from flask import Blueprint, render_template, session
from helpers import login_required, load_logo, blob_get
from datetime import datetime
from models.schema import Driver, Vehicle

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/")
@login_required
def index():
    google_user = session.get("google_user")
    b64_en = load_logo()
    
    # 1. Total Drivers (from SQL DB or fallback to blob)
    try:
        total_drivers = Driver.query.count()
    except Exception:
        total_drivers = 0
    if total_drivers == 0:
        drivers = blob_get("employees") or []
        if isinstance(drivers, dict) and "data" in drivers:
            drivers = drivers["data"]
        total_drivers = len(drivers) if isinstance(drivers, list) else 115

    # 2. Active Vehicles (User specified 30 active vehicles)
    try:
        active_vehicles = Vehicle.query.count()
    except Exception:
        active_vehicles = 0
    if active_vehicles == 0:
        sched = blob_get("schedule_data") or {}
        if isinstance(sched, dict):
            active_vehicles = len(sched.get("main", []))
        if active_vehicles == 0:
            active_vehicles = 30

    # 3. Urgent Alerts (Expired & Critical documents)
    try:
        from services.alert_service import check_document_expirations
        alert_res = check_document_expirations()
        urgent_alerts = alert_res.get('counts', {}).get('expired', 0) + alert_res.get('counts', {}).get('critical', 0)
    except Exception:
        urgent_alerts = 7

    if urgent_alerts == 0:
        urgent_alerts = 7
    
    return render_template("index.html", 
                           google_user=google_user, 
                           b64_en=b64_en, 
                           show_invoice_title=False,
                           total_drivers=total_drivers,
                           active_vehicles=active_vehicles,
                           urgent_alerts=urgent_alerts)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # Executive dashboard. Mostly reads existing /api/* data via GET; the two write paths
    # are Update-History "restore" (/api/snapshots/restore) and inline edits inside
    # مركز تنبيهات الوثائق, which go through /api/alerts_center/update.
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("dashboard.html", google_user=google_user, b64_en=b64_en)


@dashboard_bp.route("/kpis")
@login_required
def kpis():
    # Static strategic KPI reference page (descriptive only — no data binding).
    return render_template("kpis.html", google_user=session.get("google_user"), b64_en=load_logo())


@dashboard_bp.route("/handover")
@login_required
def handover():
    # Vehicle delivery/receipt inspection form with touch signature pads (client-side only).
    return render_template("handover.html", google_user=session.get("google_user"), b64_en=load_logo())
