from flask import Blueprint, render_template, session
from helpers import login_required, load_logo

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/")
@login_required
def index():
    google_user = session.get("google_user")
    b64_en = load_logo()
    # Homepage hides the "نظام الفواتير الذكي" heading (logo takes its place); the /invoice tab shows it.
    return render_template("index.html", google_user=google_user, b64_en=b64_en, show_invoice_title=False)


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
