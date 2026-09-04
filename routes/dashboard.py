# -*- coding: utf-8 -*-
"""Flask blueprint for the main dashboard and related pages."""

from datetime import datetime
from typing import Any, Dict

from flask import Blueprint, render_template, session

from helpers import login_required, load_logo, blob_get, current_branch_id
from models.schema import Driver, Vehicle

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index() -> Any:
    """Render the main index page with summary statistics."""
    try:
        google_user = session.get("google_user")
        b64_en = load_logo()
        # Branch logins see THEIR branch's numbers; admins/HQ see company-wide totals. These
        # tiles were never scoped, so a branch manager's homepage showed everyone's counts.
        bid = current_branch_id() if session.get("is_branch_user") else None

        # 1. Total Drivers (DB -> blob fallback)
        try:
            total_drivers = Driver.query.filter_by(branch_id=bid).count() if bid else Driver.query.count()
        except Exception:
            from app import db
            db.session.rollback()
            total_drivers = 0
        if total_drivers == 0:
            drivers = blob_get("employees") or []
            if isinstance(drivers, dict) and "data" in drivers:
                drivers = drivers["data"]
            total_drivers = len(drivers) if isinstance(drivers, list) else 0

        # 2. Active Vehicles (default 30)
        try:
            active_vehicles = Vehicle.query.filter_by(branch_id=bid).count() if bid else Vehicle.query.count()
        except Exception:
            from app import db
            db.session.rollback()
            active_vehicles = 0
        if active_vehicles == 0:
            sched = blob_get("schedule_data") or {}
            if isinstance(sched, dict):
                active_vehicles = len(sched.get("main", []))
            pass  # a real zero (no vehicles in DB or schedule blob) is left as 0

        # 3. Urgent Alerts (expired & critical documents)
        try:
            from services.alert_service import check_document_expirations
            alert_res: Dict[str, Any] = check_document_expirations(branch_id=bid)
            urgent_alerts = (
                alert_res.get("counts", {}).get("expired", 0)
                + alert_res.get("counts", {}).get("critical", 0)
            )
        except Exception:
            from app import db
            db.session.rollback()
            urgent_alerts = 0

        return render_template(
            "index.html",
            google_user=google_user,
            b64_en=b64_en,
            show_invoice_title=False,
            total_drivers=total_drivers,
            active_vehicles=active_vehicles,
            urgent_alerts=urgent_alerts,
        )
    except Exception:
        import traceback
        return f"<pre>{traceback.format_exc()}</pre>", 500


@dashboard_bp.route("/dashboard")
@login_required
def dashboard() -> Any:
    """Executive dashboard - mainly read-only data."""
    google_user = session.get("google_user")
    b64_en = load_logo()
    return render_template("dashboard.html", google_user=google_user, b64_en=b64_en)


@dashboard_bp.route("/kpis")
@login_required
def kpis() -> Any:
    """Static KPI reference page (descriptive only)."""
    return render_template(
        "kpis.html",
        google_user=session.get("google_user"),
        b64_en=load_logo(),
    )


@dashboard_bp.route("/handover")
@login_required
def handover() -> Any:
    """Handover page showing active branch information."""
    from helpers import current_branch_id, current_branch_name

    b_id = current_branch_id()
    b_name = current_branch_name()
    return render_template(
        "handover.html",
        active_branch_id=b_id,
        active_branch=b_name,
        google_user=session.get("google_user"),
        b64_en=load_logo(),
    )
