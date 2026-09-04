from flask import Blueprint, request, session, redirect, url_for, render_template, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import hmac
import logging
import re

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger('InvoiceApp')


def _send_account_notification(user, event):
    """Best-effort account email; never includes a password or blocks the account change."""
    from flask import current_app
    if not current_app.config.get("ACCOUNT_EMAIL_NOTIFICATIONS_ENABLED"):
        return "disabled"
    recipient = (getattr(user, "email", None) or "").strip().lower()
    if not recipient or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", recipient):
        return "missing_email"
    try:
        from flask_mail import Message
        from app import mail, _mail_send_safe
        subject = "تنبيه أمني لحسابك — BIN ZOMAH INTL."
        action = "تم إنشاء حسابك" if event == "created" else "تمت إعادة ضبط كلمة مرور حسابك"
        msg = Message(
            subject=subject,
            recipients=[recipient],
            sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
            body=(
                f"مرحبًا {user.username}،\n\n{action}. "
                "عند أول تسجيل دخول سيطلب منك النظام اختيار كلمة مرور خاصة بك. "
                "لأسباب أمنية، لا تتضمن هذه الرسالة أي كلمة مرور.\n\n"
                "إذا لم تطلب هذا الإجراء، تواصل مع مسؤول النظام فورًا."
            ),
        )
        _mail_send_safe(msg)
        logger.info("Account security email sent for user %s", user.username)
        return "sent"
    except Exception:
        logger.exception("Account security email failed for user %s", user.username)
        return "failed"


from app import login_required, role_required, limiter

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    from app import KIOSK_PASSWORD, KIOSK_USER, get_branch_accounts, get_users, BRANCH_IDS

    if session.get("authenticated"):
        if session.get("kiosk"):
            return redirect(url_for("operations.workshop"))
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        from models.schema import User
        from datetime import datetime
        from app import db

        user = None

        # Handle Kiosk override explicitly if needed
        from app import KIOSK_PASSWORD, KIOSK_USER
        if KIOSK_PASSWORD and hmac.compare_digest(username, KIOSK_USER) and hmac.compare_digest(password, KIOSK_PASSWORD):
            session.clear()
            session["authenticated"] = True
            session.permanent = True
            session["google_user"] = {"name": KIOSK_USER, "email": KIOSK_USER + "@binzomah.local"}
            session["is_admin"] = False
            session["kiosk"] = True
            logger.info("Kiosk login")
            return redirect(url_for("operations.workshop"))

        # Hardcoded master admin fallback (from ENV)
        master_user = os.environ.get("ADMIN_USERNAME", "admin")
        master_pass = os.environ.get("MASTER_PASSWORD", "123456")
        if hmac.compare_digest(username, master_user) and hmac.compare_digest(password, master_pass):
            session.clear()
            session["authenticated"] = True
            session.permanent = True
            session["user"] = username
            session["username"] = username
            session["google_user"] = {"name": username, "email": username + "@binzomah.local"}
            session["is_admin"] = True
            session["role"] = "admin"
            session["kiosk"] = False
            logger.info("Master admin login via hardcoded credentials")
            return redirect(url_for("dashboard.index"))

        # A database/schema failure must not turn the login form into a 500 for
        # the master admin fallback. Log it and continue with safe fallbacks.
        try:
            user = User.query.filter_by(username=username, is_active=True).first()
        except Exception:
            logger.exception("User lookup failed during login")
            user = None

        if user and check_password_hash(user.password_hash, password):
            user.last_login = datetime.now()
            db.session.commit()
            
            session.clear()                       # fresh session — drop any prior role/branch
            session["authenticated"] = True
            session.permanent = True
            session["user"] = user.username
            session["username"] = user.username
            session["google_user"] = {"name": user.username, "email": user.username + "@binzomah.local"}
            session["is_admin"] = (user.role == 'admin')
            session["role"] = user.role
            session["must_change_password"] = bool(getattr(user, "must_change_password", False))
            
            if user.branch_id:
                session["branch_id"] = user.branch_id
                session["is_branch_user"] = True

            session["kiosk"] = (user.role == 'kiosk')
            logger.info(f"Successful login for user: {user.username} with role: {user.role}")

            if session.get("must_change_password"):
                return redirect(url_for("auth.force_password_change"))
            if user.role == 'kiosk':
                return redirect(url_for("operations.workshop"))
            return redirect(url_for("dashboard.index"))
            
        acct = next((a for a in get_branch_accounts() if a.get("username") == username), None)
        if acct and check_password_hash(acct.get("code_hash", ""), password):
            session.clear()
            session["authenticated"] = True
            session.permanent = True
            session["user"] = username
            session["username"] = username
            session["google_user"] = {"name": username, "email": username + "@binzomah.local"}
            session["is_admin"] = False
            session["role"] = "branch_manager"
            bid = acct.get("branch_id")
            if bid in BRANCH_IDS:
                session["branch_id"] = bid
                session["is_branch_user"] = True
            logger.info(f"Branch account login: {username} -> branch {bid}")
            return redirect(url_for("dashboard.index"))

        else:
            logger.warning("Failed login attempt")
            return render_template("login.html", error="اسم المستخدم أو كلمة المرور غير صحيحة أو الحساب غير مفعل")

    return render_template("login.html")


@auth_bp.route("/force-password-change", methods=["GET", "POST"])
@login_required
def force_password_change():
    """Require a user account to choose a private password before continuing."""
    from models.schema import User
    from app import db

    username = session.get("username") or session.get("user")
    user = User.query.filter_by(username=username, is_active=True).first()
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))
    if not getattr(user, "must_change_password", False):
        return redirect(url_for("dashboard.index"))

    error = None
    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        if len(new_password) < 12:
            error = "كلمة المرور يجب أن تتكون من 12 حرفًا على الأقل"
        elif not re.search(r"[A-Z]", new_password) or not re.search(r"[a-z]", new_password) or not re.search(r"\d", new_password):
            error = "يجب أن تحتوي كلمة المرور على حرف كبير وحرف صغير ورقم"
        elif new_password != confirm:
            error = "تأكيد كلمة المرور غير مطابق"
        elif check_password_hash(user.password_hash, new_password):
            error = "اختر كلمة مرور مختلفة عن كلمة المرور الحالية"
        else:
            user.password_hash = generate_password_hash(new_password)
            user.must_change_password = False
            db.session.commit()
            session["must_change_password"] = False
            logger.info("Mandatory password change completed for user: %s", user.username)
            return redirect(url_for("dashboard.index"))

    return render_template("force_password_change.html", error=error, username=user.username)


@auth_bp.route("/logout")
def logout():
    session.clear()
    resp = redirect(url_for("auth.login"))
    resp.delete_cookie("ws_unlocked", path="/")
    return resp


@auth_bp.route("/admin/users", methods=["GET"])
@role_required("admin")
def users_admin_page():
    return render_template("users_admin.html")

@auth_bp.route("/api/users", methods=["GET", "POST", "DELETE"])
@role_required("admin")
def api_users():
    from models.schema import User, Branch
    from app import db
    import re
    from datetime import datetime

    if request.method == "GET":
        users = User.query.all()
        return jsonify({"users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email or "",
                "role": u.role,
                "is_active": u.is_active,
                "must_change_password": bool(getattr(u, "must_change_password", False)),
                "branch": u.branch.name if u.branch else "الكل",
                "branch_id": u.branch_id,
                "last_login": u.last_login.strftime("%Y-%m-%d %H:%M") if u.last_login else "-"
            }
            for u in users
        ]})
        
    body = request.get_json(silent=True) or {}
    
    if request.method == "POST":
        username = (body.get("username") or "").strip()
        password = body.get("password") or ""
        email = (body.get("email") or "").strip().lower()
        role = body.get("role") or "viewer"
        branch_id = body.get("branch_id")
        
        if not username:
            return jsonify({"error": "missing", "reason": "اسم المستخدم مطلوب"}), 400
        if not re.match(r"^[A-Za-z0-9_.@-]{2,40}$", username):
            return jsonify({"error": "bad_username", "reason": "اسم المستخدم: حروف/أرقام إنجليزية فقط"}), 400
        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            return jsonify({"error": "bad_email", "reason": "صيغة البريد الإلكتروني غير صحيحة"}), 400
            
        user = User.query.filter_by(username=username).first()
        
        if user:
            # Update existing
            if password:
                if len(password) < 12:
                    return jsonify({"error": "weak", "reason": "كلمة المرور يجب أن تكون 12 حرفًا على الأقل"}), 400
                user.password_hash = generate_password_hash(password)
                user.must_change_password = True

            user.email = email or user.email
            user.role = role
            user.branch_id = int(branch_id) if branch_id else None
            if 'is_active' in body:
                user.is_active = bool(body.get('is_active'))
            db.session.commit()
            notification = _send_account_notification(user, "reset") if password else "not_applicable"
            return jsonify({"success": True, "message": "تم التحديث بنجاح", "notification": notification})
            
        # Create new
        if not password or len(password) < 12:
            return jsonify({"error": "weak", "reason": "كلمة المرور مطلوبة (12 حرفًا على الأقل)"}), 400
            
        new_user = User(
            username=username,
            email=email or None,
            password_hash=generate_password_hash(password),
            role=role,
            branch_id=int(branch_id) if branch_id else None,
            is_active=True,
            must_change_password=True
        )
        db.session.add(new_user)
        db.session.commit()
        notification = _send_account_notification(new_user, "created")
        return jsonify({"success": True, "notification": notification})

    if request.method == "DELETE":
        user_id = body.get("id")
        user = User.query.get(user_id) if user_id else User.query.filter_by(username=(body.get("username") or "").strip()).first()
        if user:
            if user.username == "admin":
                return jsonify({"error": "لا يمكن حذف حساب المدير العام"}), 400
            db.session.delete(user)
            db.session.commit()
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "المستخدم غير موجود"}), 404


