from datetime import datetime, timedelta
from decimal import Decimal
import re

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from models.schema import Company, Payment, Subscription, SubscriptionPlan, User, db

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
    return bool(session.get("authenticated") and (session.get("is_admin") or session.get("role") == "admin"))


@saas_bp.get("/")
def landing():
    plan = SubscriptionPlan.query.filter_by(name="الأساسية", is_active=True).first()
    return render_template("saas/landing.html", plan=plan)


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
    elif Company.query.filter_by(email=email).first():
        error = "يوجد حساب شركة بهذا البريد مسبقًا"
    if error:
        return render_template("saas/register.html", error=error, form=form), 422

    now = datetime.utcnow()
    company = Company(name=name, owner_name=owner_name, phone=phone, email=email,
                      status="trial", trial_started_at=now,
                      trial_ends_at=now + timedelta(days=TRIAL_DAYS))
    db.session.add(company)
    db.session.flush()
    user = User(company_id=company.id, username=email, email=email, display_name=owner_name,
                password_hash=generate_password_hash(password), role="admin", is_active=True,
                authz_version=1)
    plan = _default_plan()
    subscription = Subscription(company=company, plan=plan, status="trial",
                                billing_cycle="monthly", started_at=now,
                                current_period_end=company.trial_ends_at)
    db.session.add_all([user, subscription])
    db.session.commit()

    session.clear()
    session.permanent = True
    session.update({"authenticated": True, "user_id": user.id, "username": user.username,
                    "user": user.username, "display_name": owner_name, "role": "admin",
                    "is_admin": False, "company_id": company.id, "authz_version": 1})
    return redirect(url_for("saas.workspace"))


@saas_bp.get("/workspace")
def workspace():
    if not session.get("authenticated") or not session.get("company_id"):
        return redirect(url_for("saas.login_redirect"))
    company = db.session.get(Company, session["company_id"])
    if not company:
        session.clear()
        return redirect(url_for("saas.register_company"))
    subscription = Subscription.query.filter_by(company_id=company.id).order_by(Subscription.id.desc()).first()
    remaining = max(0, (company.trial_ends_at - datetime.utcnow()).days) if company.status == "trial" else 0
    return render_template("saas/workspace.html", company=company, subscription=subscription,
                           remaining_days=remaining)


@saas_bp.get("/login-redirect")
def login_redirect():
    return redirect(url_for("auth.login"))


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
