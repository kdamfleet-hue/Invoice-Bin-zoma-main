from time_utils import utcnow
from datetime import timedelta
from decimal import Decimal
import re

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models.schema import Branch, Company, Payment, Subscription, SubscriptionPlan, User, db

saas_bp = Blueprint("saas", __name__)
TRIAL_DAYS = 14


def _password_error(password):
    if len(password or "") < 12:
        return "كلمة المرور يجب أن تكون 12 حرفًا على الأقل"
    if not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"\d", password):
        return "يجب أن تحتوي كلمة المرور على حرف كبير وحرف صغير ورقم"
    return None


def _default_plan():
    plan = SubscriptionPlan.query.filter_by(name="الأساسية").first()
    if not plan:
        plan = SubscriptionPlan(
            name="الأساسية", monthly_price=Decimal("99.00"), annual_price=Decimal("990.00"),
            description="إدارة الأسطول والتشغيل والمستندات للمؤسسات الصغيرة والمتوسطة.",
        )
        db.session.add(plan)
        db.session.flush()
    return plan


def _central_admin_required():
    # A self-registered company's own owner also gets role="admin" (below) to manage
    # ITS OWN company — that must never satisfy the PLATFORM admin check. Real platform
    # admins are legacy staff logins, which never carry company_id.
    return bool(session.get("authenticated") and not session.get("company_id")
                and (session.get("is_admin") or session.get("role") == "admin"))


def _enter_isolated_site(user, company):
    session.clear()
    session.permanent = True
    session.update({
        "authenticated": True,
        "user_id": user.id,
        "username": user.username,
        "user": user.username,
        "display_name": user.display_name or company.name,
        "role": user.role or "admin",
        "is_admin": False,
        "company_id": company.id,
        "authz_version": int(getattr(user, "authz_version", 1) or 1),
        "kiosk": False,
        "google_user": {
            "name": user.display_name or company.name,
            "email": user.email or user.username,
        },
    })
    # Guarantees branch_id even for a legacy account created before per-company
    # branches existed (self-heals instead of leaving it unset, which
    # current_branch_id() would otherwise have to fail closed on). Never let a
    # failure here (e.g. an unexpected DB error) turn a login into a 500 --
    # current_branch_id()'s fail-closed sentinel keeps a still-unhealed session
    # from ever reaching real data either way.
    from helpers import ensure_company_branch
    try:
        session["branch_id"] = ensure_company_branch(user)
        session["is_branch_user"] = True
    except Exception:
        current_app.logger.exception("ensure_company_branch failed for user %s", user.id)
        db.session.rollback()
    # Not dashboard.index: that's the legacy single-company app, which a company
    # session is now explicitly blocked from (see app.py _block_company_sessions_from_legacy_app).
    return redirect(url_for("saas.workspace"))


def _send_login_alert(user, company):
    """Best-effort alert for a successful company login; never includes secrets."""
    from flask import current_app

    if not current_app.config.get("LOGIN_EMAIL_ALERTS_ENABLED"):
        return "disabled"
    recipient = (getattr(user, "email", None) or "").strip().lower()
    if not recipient or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", recipient):
        return "missing_email"
    try:
        from flask_mail import Message
        from app import _mail_send_safe

        now = utcnow().strftime("%Y-%m-%d %H:%M UTC")
        ip = request.headers.get("CF-Connecting-IP") or request.remote_addr or "غير معروف"
        user_agent = (request.user_agent.string or "غير معروف")[:240]
        msg = Message(
            subject="تنبيه أمني: تسجيل دخول جديد إلى حساب KM",
            recipients=[recipient],
            sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
            body=(
                f"مرحبًا {user.display_name or user.username}،\n\n"
                "تم تسجيل دخول ناجح إلى مساحة شركتك في KM.\n\n"
                f"الشركة: {company.name}\n"
                f"الوقت: {now}\n"
                f"عنوان الشبكة: {ip}\n"
                f"المتصفح: {user_agent}\n\n"
                "إذا لم تكن أنت، غيّر كلمة المرور فورًا وتواصل مع مسؤول النظام.\n"
                "لا تتضمن هذه الرسالة كلمة المرور أو أي رمز سري."
            ),
        )
        _mail_send_safe(msg)
        return "sent"
    except Exception:
        current_app.logger.exception("Login alert email failed for user %s", user.username)
        return "failed"


@saas_bp.get("/")
def landing():
    plan = SubscriptionPlan.query.filter_by(name="الأساسية", is_active=True).first()
    return render_template("saas/landing.html", plan=plan)


@saas_bp.get("/highlights")
def highlights():
    return render_template("saas/highlights.html")


@saas_bp.route("/saas-login", methods=["GET", "POST"])
def company_login():
    if session.get("authenticated") and session.get("company_id"):
        return redirect(url_for("dashboard.index"))
    if request.method == "GET":
        message = "تم تحديث كلمة المرور بنجاح. يمكنك تسجيل الدخول الآن." if request.args.get("reset") == "success" else None
        return render_template("saas/login.html", message=message)
    identifier = (request.form.get("email") or request.form.get("username") or "").strip().lower()
    password = request.form.get("password", "")
    if not identifier or not password:
        return render_template("saas/login.html", error="أدخل البريد وكلمة المرور"), 422
    user = User.query.filter(
        db.or_(db.func.lower(User.email) == identifier, db.func.lower(User.username) == identifier),
        User.is_active.is_(True),
    ).first()
    if not user or not user.password_hash or not check_password_hash(user.password_hash, password):
        return render_template("saas/login.html", error="بيانات الدخول غير صحيحة"), 401
    company = db.session.get(Company, user.company_id) if user.company_id else None
    if not company:
        return render_template("saas/login.html", error="هذا الحساب غير مرتبط بشركة."), 403
    if company.status == "suspended":
        return render_template("saas/login.html", error="حساب الشركة موقوف."), 403
    user.last_login = utcnow()
    db.session.commit()
    _send_login_alert(user, company)
    return _enter_isolated_site(user, company)


@saas_bp.route("/register", methods=["GET", "POST"])
def register_company():
    if request.method == "GET":
        return render_template("saas/register.html")
    form = request.form
    name = form.get("company_name", "").strip()[:180]
    owner_name = form.get("owner_name", "").strip()[:150]
    phone = form.get("phone", "").strip()[:30]
    email = form.get("email", "").strip().lower()[:255]
    password = form.get("password", "")
    confirmation = form.get("password_confirmation", "")
    error = _password_error(password)
    if not all((name, owner_name, phone, email, password)):
        error = "جميع الحقول مطلوبة"
    elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        error = "أدخل بريدًا إلكترونيًا صحيحًا"
    elif password != confirmation:
        error = "تأكيد كلمة المرور غير مطابق"
    elif Company.query.filter_by(email=email).first() or User.query.filter(
        db.or_(db.func.lower(User.email) == email, db.func.lower(User.username) == email)
    ).first():
        error = "يوجد حساب بهذا البريد مسبقًا. استخدم بريدًا آخر أو سجّل الدخول."
    if error:
        return render_template("saas/register.html", error=error, form=form), 422
    now = utcnow()
    company = Company(name=name, owner_name=owner_name, phone=phone, email=email,
                      status="trial", trial_started_at=now,
                      trial_ends_at=now + timedelta(days=TRIAL_DAYS))
    db.session.add(company)
    db.session.flush()
    # This company's own isolated operational space — never one of البن زومة's real
    # 6 branches (see models/schema.py Branch.company_id). Reuses the existing,
    # tested branch_id-based scoping.py enforcement instead of a second isolation
    # mechanism; current_branch_id() (helpers.py/app.py) knows to trust this id only
    # for this exact company's own session.
    branch = Branch(name=f"مساحة {name}", company_id=company.id)
    db.session.add(branch)
    db.session.flush()
    user = User(company_id=company.id, branch_id=branch.id, username=email, email=email, phone=phone,
                display_name=owner_name, password_hash=generate_password_hash(password), role="admin",
                is_active=True, authz_version=1)
    plan = _default_plan()
    subscription = Subscription(company=company, plan=plan, status="trial",
                                billing_cycle="monthly", started_at=now,
                                current_period_end=company.trial_ends_at)
    db.session.add_all([user, subscription])
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        # Do not expose database details to the user. The common production
        # case is a duplicate email submitted concurrently with another form.
        current_app.logger.exception("Company registration failed for email %s", email)
        duplicate = Company.query.filter_by(email=email).first() or User.query.filter(
            db.or_(db.func.lower(User.email) == email, db.func.lower(User.username) == email)
        ).first()
        if duplicate:
            error = "يوجد حساب بهذا البريد مسبقًا. استخدم بريدًا آخر أو سجّل الدخول."
        else:
            error = "تعذر إنشاء الحساب الآن. حاول مرة أخرى، وإذا تكرر الخطأ تواصل مع الدعم."
        return render_template("saas/register.html", error=error, form=form), 422
    _enter_isolated_site(user, company)
    return redirect(url_for("saas.workspace"))


@saas_bp.get("/workspace")
def workspace():
    if not session.get("authenticated") or not session.get("company_id"):
        return redirect(url_for("saas.company_login"))
    company = db.session.get(Company, session["company_id"])
    if not company:
        session.clear()
        return redirect(url_for("saas.register_company"))
    subscription = Subscription.query.filter_by(company_id=company.id).order_by(Subscription.id.desc()).first()
    remaining = max(0, (company.trial_ends_at - utcnow()).days) if company.status == "trial" else 0
    return render_template("saas/workspace.html", company=company, subscription=subscription,
                           remaining_days=remaining)


TRIAL_TABS = [
    {"href": "/fleet_dashboard", "icon": "📊", "title": "لوحة الأسطول", "desc": "نظرة عامة على المركبات والسائقين والتنبيهات"},
    {"href": "/drivers_info", "icon": "🧑‍✈️", "title": "بيانات السائقين", "desc": "سجلّ السائقين وربطهم بالمركبات"},
    {"href": "/driver-vehicle-assignments", "icon": "🔗", "title": "ربط السائق بالمركبة", "desc": "تعيين ونقل عهدة المركبات"},
    {"href": "/schedule", "icon": "📅", "title": "الجدول الأسبوعي", "desc": "جدولة حركة الأسطول أسبوعيًا"},
    {"href": "/custody", "icon": "📦", "title": "العهد", "desc": "عهد السائقين ومتابعتها"},
    {"href": "/handover", "icon": "🤝", "title": "التسليم والاستلام", "desc": "سجلّ تسليم واستلام المركبات"},
    {"href": "/yard", "icon": "🅿️", "title": "الساحة", "desc": "حالة المركبات داخل وخارج الساحة"},
    {"href": "/workshop", "icon": "🔧", "title": "الورشة", "desc": "أوامر الصيانة وقطع الغيار"},
    {"href": "/oils", "icon": "🛢️", "title": "الزيوت والفلاتر", "desc": "متابعة صيانة الزيوت الدورية"},
    {"href": "/purchase", "icon": "🧾", "title": "طلبات الشراء", "desc": "أوامر الشراء ومتابعتها"},
    {"href": "/washing", "icon": "🧼", "title": "الغسيل", "desc": "جدولة غسيل المركبات"},
    {"href": "/incidents", "icon": "⚠️", "title": "الحوادث والمخالفات", "desc": "تسجيل ومتابعة الحوادث"},
    {"href": "/records", "icon": "🗂️", "title": "التوثيق", "desc": "أرشيف السجلات التشغيلية"},
    {"href": "/insights", "icon": "🧠", "title": "التحليلات", "desc": "مؤشرات تشغيلية مجمّعة"},
    {"href": "/kpis", "icon": "📈", "title": "مؤشرات الأداء", "desc": "دليل مؤشرات الأداء الرئيسية"},
]


@saas_bp.get("/company-platform")
def company_platform():
    """A company's own platform area — real navigation to the operational tabs
    individually verified safe for a company session (see app.py
    _SAAS_TRIAL_TAB_PATHS and the scoping/route fixes it depends on). Anything
    NOT listed here either isn't company-isolated yet (no safe path exists) or
    is explicitly excluded (real GPS device data, the unbranched legacy HR table)
    — never send a company session to the legacy single-company dashboard itself.
    """
    if not session.get("authenticated") or not session.get("company_id"):
        return redirect(url_for("saas.company_login"))
    company = db.session.get(Company, session["company_id"])
    if not company:
        session.clear()
        return redirect(url_for("saas.register_company"))
    trial_active = company.status == "active" or (
        company.status == "trial" and bool(company.trial_ends_at) and utcnow() <= company.trial_ends_at
    )
    return render_template("saas/company_platform.html", company=company, tabs=TRIAL_TABS,
                           trial_active=trial_active)


@saas_bp.get("/login-redirect")
def login_redirect():
    return redirect(url_for("saas.company_login"))


@saas_bp.get("/plans")
def plans():
    plans = SubscriptionPlan.query.filter_by(is_active=True).order_by(SubscriptionPlan.id).all()
    if not plans:
        plan = _default_plan()
        db.session.commit()
        plans = [plan]
    return render_template("saas/plans.html", plans=plans)


@saas_bp.get("/platform-admin")
def central_admin():
    if not _central_admin_required():
        return redirect(url_for("auth.login"))
    companies = Company.query.order_by(Company.created_at.desc()).all()
    counts = {
        "companies": len(companies),
        "trials": sum(c.status == "trial" for c in companies),
        "active": sum(c.status == "active" for c in companies),
        "expired": sum(c.status == "expired" for c in companies),
    }
    plans = SubscriptionPlan.query.order_by(SubscriptionPlan.id).all()
    return render_template("saas/admin.html", companies=companies, counts=counts, plans=plans)


@saas_bp.post("/platform-admin/company/<int:company_id>/status")
def central_company_status(company_id):
    if not _central_admin_required():
        return "غير مصرح", 403
    company = db.session.get(Company, company_id)
    if not company:
        return "الشركة غير موجودة", 404
    status = request.form.get("status", "").strip()
    if status not in {"trial", "active", "suspended", "expired"}:
        return "حالة غير صالحة", 400
    company.status = status
    db.session.commit()
    flash("تم تحديث حالة الشركة", "success")
    return redirect(url_for("saas.central_admin"))


@saas_bp.post("/platform-admin/plan")
def central_create_plan():
    if not _central_admin_required():
        return "غير مصرح", 403
    name = request.form.get("name", "").strip()[:100]
    price = request.form.get("monthly_price", "").strip()
    if not name or SubscriptionPlan.query.filter_by(name=name).first():
        flash("اسم الباقة مطلوب وغير مكرر", "danger")
        return redirect(url_for("saas.central_admin"))
    try:
        monthly = Decimal(price)
    except Exception:
        flash("قيمة الباقة غير صحيحة", "danger")
        return redirect(url_for("saas.central_admin"))
    db.session.add(SubscriptionPlan(name=name, monthly_price=monthly,
                                    annual_price=monthly * Decimal("10"),
                                    description=request.form.get("description", "").strip()[:500]))
    db.session.commit()
    flash("تم إنشاء الباقة", "success")
    return redirect(url_for("saas.central_admin"))


@saas_bp.get("/platform-admin/payments")
def central_payments():
    if not _central_admin_required():
        return redirect(url_for("auth.login"))
    payments = Payment.query.order_by(Payment.created_at.desc()).limit(100).all()
    return render_template("saas/payments.html", payments=payments)
