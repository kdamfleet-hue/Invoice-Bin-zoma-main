# -*- coding: utf-8 -*-
"""Flask blueprint for the main dashboard and related pages."""

from datetime import datetime
from typing import Any, Dict
import logging

from flask import Blueprint, render_template, session

from helpers import login_required, load_logo, blob_get, current_branch_id
from models.schema import Driver, Vehicle

dashboard_bp = Blueprint("dashboard", __name__)
logger = logging.getLogger("InvoiceApp")


# Presentation-only home presets. Route authorization remains enforced by the
# existing server-side decorators; these settings only reduce visual clutter.
ROLE_HOME_CONFIG = {
    "admin": {
        "key": "admin", "role_label": "مدير النظام", "title": "مركز القرار",
        "description": "ابدأ بأهم الاستثناءات، ثم انتقل إلى القرارات والتحليلات الإدارية.",
        "primary": {"label": "مراجعة الإجراءات الحرجة", "href": "/alerts", "icon": "shield-alert"},
        "metrics": [
            {"key": "urgent_alerts", "label": "تنبيهات تحتاج قرارًا", "detail": "وثائق أو حالات عاجلة", "href": "/alerts", "icon": "shield-alert", "tone": "danger"},
            {"key": "active_vehicles", "label": "المركبات النشطة", "detail": "من بيانات الأسطول", "href": "/fleet_dashboard", "icon": "truck", "tone": "mint"},
            {"key": "total_drivers", "label": "الأفراد والسائقون", "detail": "السجل التشغيلي الموحد", "href": "/employees", "icon": "users", "tone": "gold"},
        ],
        "tasks": [
            {"label": "مراجعة تنبيهات الوثائق", "note": "الأولوية الأولى قبل القرارات اليومية", "href": "/alerts"},
            {"label": "قراءة مؤشرات الأداء", "note": "ملخص الجاهزية والاستثناءات", "href": "/kpis"},
            {"label": "فتح التحليلات التشغيلية", "note": "التفاصيل المصدرية للفرع", "href": "/insights"},
        ],
        "workspaces": [
            {"label": "لوحة المدير", "note": "القرارات والرقابة", "href": "/admin", "icon": "layout-dashboard"},
            {"label": "لوحة الأسطول", "note": "المركبات والتنبيهات", "href": "/fleet_dashboard", "icon": "truck"},
            {"label": "التحليلات", "note": "قراءة مؤشرات الأداء", "href": "/insights", "icon": "chart-no-axes-combined"},
            {"label": "تقرير الأداء", "note": "سرعة وتحويل الدخول", "href": "/performance-report", "icon": "gauge"},
        ],
    },
    "branch_manager": {
        "key": "branch_manager", "role_label": "مدير الفرع", "title": "خطة الفرع اليوم",
        "description": "شاهد حالة الفرع، ثم ابدأ بتوزيع الحركة أو معالجة الاستثناءات.",
        "primary": {"label": "فتح دورة التشغيل", "href": "/ops", "icon": "settings-2"},
        "metrics": [
            {"key": "urgent_alerts", "label": "تنبيهات الفرع", "detail": "عناصر تحتاج متابعة", "href": "/fleet_dashboard", "icon": "triangle-alert", "tone": "danger"},
            {"key": "active_vehicles", "label": "المركبات النشطة", "detail": "ضمن نطاق الفرع", "href": "/fleet_dashboard", "icon": "truck", "tone": "mint"},
            {"key": "total_drivers", "label": "الطاقم التشغيلي", "detail": "الأفراد والسائقون", "href": "/drivers_info", "icon": "users", "tone": "gold"},
        ],
        "tasks": [
            {"label": "فتح دورة التشغيل", "note": "راجع الخطة والاستثناءات اليومية", "href": "/ops"},
            {"label": "متابعة المركبات الحية", "note": "راقب الحركة الميدانية", "href": "/tracking"},
            {"label": "مراجعة التسليم والاستلام", "note": "تأكد من إغلاق العمليات المفتوحة", "href": "/handover"},
        ],
        "workspaces": [
            {"label": "دورة التشغيل", "note": "الخطة والاستثناءات", "href": "/ops", "icon": "settings-2"},
            {"label": "التتبع الحي", "note": "مواقع المركبات", "href": "/tracking", "icon": "map-pinned"},
            {"label": "التسليم والاستلام", "note": "سجل العهد", "href": "/handover", "icon": "key-round"},
        ],
    },
    "operations": {
        "key": "operations", "role_label": "التشغيل والحركة", "title": "خطة الحركة اليوم",
        "description": "ابدأ بالرحلات وتوزيع المركبات، ثم تابع الاستثناءات في الميدان.",
        "primary": {"label": "تخصيص رحلات اليوم", "href": "/schedule/transport", "icon": "route"},
        "metrics": [
            {"key": "urgent_alerts", "label": "استثناءات التشغيل", "detail": "تظهر ضمن لوحة الأسطول", "href": "/fleet_dashboard", "icon": "triangle-alert", "tone": "danger"},
            {"key": "active_vehicles", "label": "المركبات النشطة", "detail": "المتاحة للتشغيل", "href": "/dammam", "icon": "truck", "tone": "mint"},
            {"key": "total_drivers", "label": "الأفراد والسائقون", "detail": "طاقم الحركة", "href": "/drivers_info", "icon": "users", "tone": "gold"},
        ],
        "tasks": [
            {"label": "توزيع رحلات النقل", "note": "خصص السائق والمركبة", "href": "/schedule/transport"},
            {"label": "فتح التتبع الحي", "note": "تابع المواقع والاستثناءات", "href": "/tracking"},
            {"label": "مراجعة حركة المركبات", "note": "تابع الحالة من التتبع الحي", "href": "/tracking"},
        ],
        "workspaces": [
            {"label": "الجدول الأسبوعي", "note": "توزيع الحركة", "href": "/schedule", "icon": "calendar-days"},
            {"label": "نقل عام وخاص", "note": "الرحلات والتخصيص", "href": "/schedule/transport", "icon": "route"},
            {"label": "التتبع الحي", "note": "مواقع المركبات", "href": "/tracking", "icon": "map-pinned"},
        ],
    },
    "maintenance": {
        "key": "maintenance", "role_label": "الصيانة", "title": "أولوية الورشة",
        "description": "انتقل مباشرة إلى أوامر العمل والمخزون بدل التنقل بين أقسام النظام.",
        "primary": {"label": "فتح أوامر الورشة", "href": "/workshop", "icon": "wrench"},
        "metrics": [
            {"key": "urgent_alerts", "label": "حالات تشغيلية", "detail": "تظهر ضمن لوحة الأسطول", "href": "/fleet_dashboard", "icon": "triangle-alert", "tone": "danger"},
            {"key": "active_vehicles", "label": "المركبات النشطة", "detail": "مدخل لحالة الأسطول", "href": "/dammam", "icon": "truck", "tone": "mint"},
            {"key": "total_drivers", "label": "الأفراد والسائقون", "detail": "للتنسيق التشغيلي", "href": "/drivers_info", "icon": "users", "tone": "gold"},
        ],
        "tasks": [
            {"label": "مراجعة أوامر الورشة", "note": "ابدأ بالمهام المفتوحة", "href": "/workshop"},
            {"label": "مراجعة قطع الغيار", "note": "افحص الاحتياج قبل العمل", "href": "/spare_parts"},
            {"label": "تسجيل المحروقات", "note": "حدّث الاستهلاك التشغيلي", "href": "/fuel"},
        ],
        "workspaces": [
            {"label": "الورشة", "note": "صيانة وإصلاح", "href": "/workshop", "icon": "wrench"},
            {"label": "المحروقات", "note": "تموين واستهلاك", "href": "/fuel", "icon": "fuel"},
            {"label": "قطع الغيار", "note": "المخزون الفني", "href": "/spare_parts", "icon": "package"},
            {"label": "الإطارات", "note": "المخزون والحالة", "href": "/inventory/tires", "icon": "circle-dot"},
        ],
    },
    "finance": {
        "key": "finance", "role_label": "المالية", "title": "مراجعة المعاملات",
        "description": "ابدأ بما يحتاج مراجعة مالية، مع إبقاء المسارات التشغيلية الثانوية خارج الواجهة الأولى.",
        "primary": {"label": "فتح الفواتير", "href": "/invoice", "icon": "receipt-text"},
        "metrics": [
            {"key": "urgent_alerts", "label": "حالات تتطلب متابعة", "detail": "تظهر ضمن لوحة الأسطول", "href": "/fleet_dashboard", "icon": "triangle-alert", "tone": "danger"},
            {"key": "active_vehicles", "label": "المركبات النشطة", "detail": "مرجع لمصروفات التشغيل", "href": "/dammam", "icon": "truck", "tone": "mint"},
            {"key": "total_drivers", "label": "الأفراد والسائقون", "detail": "مرجع للحركة والعهد", "href": "/drivers_info", "icon": "users", "tone": "gold"},
        ],
        "tasks": [
            {"label": "مراجعة الفواتير", "note": "المعاملات المسجلة", "href": "/invoice"},
            {"label": "فتح المشتريات", "note": "الطلبات والموافقات", "href": "/purchase"},
            {"label": "مراجعة السجلات المالية", "note": "المعاملات المؤرشفة", "href": "/records"},
        ],
        "workspaces": [
            {"label": "الفواتير", "note": "المعاملات المالية", "href": "/invoice", "icon": "receipt-text"},
            {"label": "المشتريات", "note": "الطلبات", "href": "/purchase", "icon": "shopping-cart"},
            {"label": "سجل التدقيق", "note": "تتبع التغييرات", "href": "/audit-log", "icon": "shield-check"},
            {"label": "السجلات", "note": "المعاملات المؤرشفة", "href": "/records", "icon": "folder-archive"},
        ],
    },
    "data_entry": {
        "key": "data_entry", "role_label": "إدخال البيانات", "title": "جودة السجل التشغيلي",
        "description": "أكمل البيانات الناقصة واربط السائقين بالمركبات من مسار عمل واضح.",
        "primary": {"label": "فتح جودة البيانات", "href": "/data-quality", "icon": "database-zap"},
        "metrics": [
            {"key": "urgent_alerts", "label": "سجلات تحتاج استكمالًا", "detail": "ابدأ من جودة البيانات", "href": "/data-quality", "icon": "triangle-alert", "tone": "danger"},
            {"key": "total_drivers", "label": "الأفراد والسائقون", "detail": "السجل المرجعي", "href": "/drivers_info", "icon": "users", "tone": "gold"},
            {"key": "active_vehicles", "label": "المركبات النشطة", "detail": "السجل المرجعي للمركبات", "href": "/dammam", "icon": "truck", "tone": "mint"},
        ],
        "tasks": [
            {"label": "معالجة جودة البيانات", "note": "ابدأ بالسجلات غير المكتملة", "href": "/data-quality"},
            {"label": "ربط سائق بمركبة", "note": "حدّث التخصيص التشغيلي", "href": "/driver-vehicle-assignments"},
            {"label": "مراجعة الوثائق", "note": "أكمل الملفات الناقصة", "href": "/documents"},
        ],
        "workspaces": [
            {"label": "جودة البيانات", "note": "السجلات الناقصة", "href": "/data-quality", "icon": "badge-check"},
            {"label": "ربط السائق", "note": "التخصيص التشغيلي", "href": "/driver-vehicle-assignments", "icon": "link"},
            {"label": "السائقون", "note": "الملفات المرجعية", "href": "/drivers_info", "icon": "contact-round"},
            {"label": "الوثائق", "note": "الأرشيف", "href": "/documents", "icon": "folder-open"},
        ],
    },
    "viewer": {
        "key": "viewer", "role_label": "مستخدم للقراءة", "title": "ملخص الحالة",
        "description": "اطلع على الجاهزية والمؤشرات ثم انتقل إلى التفاصيل المسموح بها.",
        "primary": {"label": "فتح لوحة الأسطول", "href": "/fleet_dashboard", "icon": "layout-dashboard"},
        "metrics": [
            {"key": "urgent_alerts", "label": "حالة تشغيلية", "detail": "تظهر ضمن لوحة الأسطول", "href": "/fleet_dashboard", "icon": "triangle-alert", "tone": "danger"},
            {"key": "active_vehicles", "label": "المركبات النشطة", "detail": "الحالة الحالية للأسطول", "href": "/fleet_dashboard", "icon": "truck", "tone": "mint"},
            {"key": "total_drivers", "label": "الأفراد والسائقون", "detail": "السجل الموحد", "href": "/drivers_info", "icon": "users", "tone": "gold"},
        ],
        "tasks": [
            {"label": "قراءة لوحة الأسطول", "note": "الحالة والتفاصيل", "href": "/fleet_dashboard"},
            {"label": "فتح مؤشرات الأداء", "note": "مؤشرات وصفية", "href": "/kpis"},
            {"label": "مراجعة التحليلات", "note": "القراءة المصدرية", "href": "/insights"},
        ],
        "workspaces": [
            {"label": "لوحة الأسطول", "note": "الحالة التشغيلية", "href": "/fleet_dashboard", "icon": "truck"},
            {"label": "مؤشرات الأداء", "note": "ملخص وصفي", "href": "/kpis", "icon": "chart-no-axes-combined"},
            {"label": "التحليلات", "note": "التفاصيل", "href": "/insights", "icon": "brain"},
            {"label": "السجلات", "note": "القراءة المسموحة", "href": "/records", "icon": "folder-archive"},
        ],
    },
    "kiosk": {
        "key": "kiosk", "role_label": "محطة ميدانية", "title": "عملية ميدانية سريعة",
        "description": "ابدأ بإجراء النقل أو الساحة، ثم أنهِ العملية دون ازدحام في الخيارات.",
        "primary": {"label": "فتح تطبيق النقل", "href": "/m/transport", "icon": "smartphone"},
        "metrics": [
            {"key": "urgent_alerts", "label": "تنبيهات اليوم", "detail": "تحتاج انتباهًا", "href": "/fleet_dashboard", "icon": "triangle-alert", "tone": "danger"},
            {"key": "active_vehicles", "label": "مركبات نشطة", "detail": "الحالة الحالية", "href": "/dammam", "icon": "truck", "tone": "mint"},
            {"key": "total_drivers", "label": "الطاقم", "detail": "العدد التشغيلي", "href": "/drivers_info", "icon": "users", "tone": "gold"},
        ],
        "tasks": [
            {"label": "بدء عملية النقل", "note": "التطبيق الميداني", "href": "/m/transport"},
            {"label": "مراجعة التسليم", "note": "الاستلام والعهد", "href": "/handover"},
            {"label": "فتح دورة التشغيل", "note": "مرجع العمليات اليومية", "href": "/ops"},
        ],
        "workspaces": [
            {"label": "تطبيق النقل", "note": "تنفيذ ميداني", "href": "/m/transport", "icon": "smartphone"},
            {"label": "التسليم", "note": "استلام وعهد", "href": "/handover", "icon": "key-round"},
            {"label": "دورة التشغيل", "note": "مرجع العمليات", "href": "/ops", "icon": "settings-2"},
            {"label": "لوحة الأسطول", "note": "حالة المركبات", "href": "/fleet_dashboard", "icon": "truck"},
        ],
    },
}


def _role_home_profile(role: str | None) -> Dict[str, Any]:
    """Return a safe, presentation-only home profile for the authenticated role."""
    return ROLE_HOME_CONFIG.get(role or "viewer", ROLE_HOME_CONFIG["viewer"])


@dashboard_bp.route("/")
@login_required
def index() -> Any:
    """Render the main index page with summary statistics."""
    try:
        google_user = session.get("google_user")
        home_profile = _role_home_profile(session.get("role"))
        # Branch logins see THEIR branch's numbers; admins/HQ see company-wide totals. These
        # tiles were never scoped, so a branch manager's homepage showed everyone's counts.
        bid = current_branch_id() if session.get("is_branch_user") else None

        # Use the shared read-only insights aggregation so homepage and fleet dashboard
        # expose the same source-aware numbers.
        try:
            from app import _compute_insights
            from app import _ttl_cached
            cache_scope = "branch:%s" % (bid if bid is not None else "all")
            insight_view = _ttl_cached(
                "home_insights:%s" % cache_scope,
                10,
                lambda: _compute_insights(rid=bid),
            )
            total_drivers = insight_view.get("people", {}).get("reconciled_total", 0)
            active_vehicles = insight_view.get("fleet", {}).get("vehicles", 0)
            urgent_alerts = (insight_view.get("documents", {}).get("expired", 0)
                             + insight_view.get("documents", {}).get("d30", 0))
            return render_template(
                "index.html",
                google_user=google_user,
                show_invoice_title=False,
                total_drivers=total_drivers,
                active_vehicles=active_vehicles,
                urgent_alerts=urgent_alerts,
                truth_center=insight_view,
                home_profile=home_profile,
            )
        except Exception as shared_exc:
            logger.warning("Shared truth-center aggregation unavailable: %s", shared_exc)

        # Legacy fallback below remains read-only for partial deployments.
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
            show_invoice_title=False,
            total_drivers=total_drivers,
            active_vehicles=active_vehicles,
            urgent_alerts=urgent_alerts,
            truth_center=None,
            home_profile=home_profile,
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
