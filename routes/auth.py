from flask import Blueprint, request, session, redirect, url_for, render_template, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import hmac
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger('InvoiceApp')

from app import login_required, role_required

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from app import KIOSK_PASSWORD, KIOSK_USER, get_branch_accounts, get_users, BRANCH_IDS

    if session.get("authenticated"):
        if session.get("kiosk"):
            return redirect(url_for("workshop"))
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        from models.schema import User
        from datetime import datetime
        from app import db

        user = User.query.filter_by(username=username, is_active=True).first()

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
            return redirect(url_for("workshop"))

        if user and check_password_hash(user.password_hash, password):
            user.last_login = datetime.now()
            db.session.commit()
            
            session.clear()                       # fresh session — drop any prior role/branch
            session["authenticated"] = True
            session.permanent = True
            session["google_user"] = {"name": user.username, "email": user.username + "@binzomah.local"}
            session["is_admin"] = (user.role == 'admin')
            session["role"] = user.role
            
            if user.branch_id:
                session["branch_id"] = user.branch_id
                session["is_branch_user"] = True

            session["kiosk"] = (user.role == 'kiosk')
            logger.info(f"Successful login for user: {user.username} with role: {user.role}")
            
            if user.role == 'kiosk':
                return redirect(url_for("workshop"))
            return redirect(url_for("index"))
            
        else:
            logger.warning("Failed login attempt")
            return render_template("login.html", error="اسم المستخدم أو كلمة المرور غير صحيحة أو الحساب غير مفعل")

    return render_template("login.html")


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
                "role": u.role,
                "is_active": u.is_active,
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
        role = body.get("role") or "viewer"
        branch_id = body.get("branch_id")
        
        if not username:
            return jsonify({"error": "missing", "reason": "اسم المستخدم مطلوب"}), 400
        if not re.match(r"^[A-Za-z0-9_.@-]{2,40}$", username):
            return jsonify({"error": "bad_username", "reason": "اسم المستخدم: حروف/أرقام إنجليزية فقط"}), 400
            
        user = User.query.filter_by(username=username).first()
        
        if user:
            # Update existing
            if password:
                if len(password) < 4:
                    return jsonify({"error": "weak", "reason": "كلمة المرور قصيرة جداً"}), 400
                user.password_hash = generate_password_hash(password)
            user.role = role
            user.branch_id = int(branch_id) if branch_id else None
            if 'is_active' in body:
                user.is_active = bool(body.get('is_active'))
            db.session.commit()
            return jsonify({"success": True, "message": "تم التحديث بنجاح"})
            
        # Create new
        if not password or len(password) < 4:
            return jsonify({"error": "weak", "reason": "كلمة المرور مطلوبة (4 أحرف على الأقل)"}), 400
            
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            branch_id=int(branch_id) if branch_id else None,
            is_active=True
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"success": True})

    if request.method == "DELETE":
        user_id = body.get("id")
        user = User.query.get(user_id)
        if user:
            if user.username == "admin":
                return jsonify({"error": "لا يمكن حذف حساب المدير العام"}), 400
            db.session.delete(user)
            db.session.commit()
        return jsonify({"success": True})


