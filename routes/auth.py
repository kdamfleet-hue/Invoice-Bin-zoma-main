from app import login_required
from flask import Blueprint, request, session, redirect, url_for, render_template, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import hmac
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger('InvoiceApp')

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

        # Kiosk account: workshop-only, no nav. Check first (constant-time, no DB needed).
        if KIOSK_PASSWORD and hmac.compare_digest(username, KIOSK_USER) and hmac.compare_digest(password, KIOSK_PASSWORD):
            session.clear()
            session["authenticated"] = True
            session.permanent = True
            session["google_user"] = {"name": KIOSK_USER, "email": KIOSK_USER + "@binzomah.local"}
            session["is_admin"] = False
            session["kiosk"] = True
            logger.info("Kiosk login")
            return redirect(url_for("workshop"))

        master_user = os.environ.get("ADMIN_USERNAME", "admin")
        master_pass = os.environ.get("MASTER_PASSWORD", "123456")

        # 1) Master/HQ admin (constant-time)  2) a per-branch account (locked to its branch)
        # 3) a general shared account.
        authed_name = None
        is_admin = False
        branch_id = None
        if hmac.compare_digest(username, master_user) and hmac.compare_digest(password, master_pass):
            authed_name = username
            is_admin = True
        else:
            for a in get_branch_accounts():
                if a.get("username") == username and a.get("code_hash") and check_password_hash(a["code_hash"], password):
                    authed_name = username
                    branch_id = a.get("branch_id")
                    break
            if not authed_name:
                for u in get_users():
                    if u.get("username") == username and u.get("pw_hash") and check_password_hash(u["pw_hash"], password):
                        authed_name = u.get("name") or username
                        break
        if authed_name:
            session.clear()                       # fresh session — drop any prior role/branch
            session["authenticated"] = True
            session.permanent = True
            session["google_user"] = {"name": authed_name, "email": (username or "user") + "@binzomah.local"}
            session["is_admin"] = is_admin
            if branch_id in BRANCH_IDS:
                session["branch_id"] = branch_id
                session["is_branch_user"] = True
            logger.info("Successful login")
            return redirect(url_for("index"))
        else:
            logger.warning("Failed login attempt")
            return render_template("login.html", error="اسم المستخدم أو كلمة المرور غير صحيحة")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    resp = redirect(url_for("login"))
    resp.delete_cookie("ws_unlocked", path=WS_PREFIX)
    return resp


@login_required
def api_users():
    from app import get_users, set_users, _audit_add, login_required

    # Manage shared login accounts — only reachable from the unlocked Settings tab.
    if not session.get("settings_unlocked"):
        return jsonify({"error": "locked"}), 403
    if request.method == "GET":
        return jsonify({"users": [
            {"username": u.get("username"), "name": u.get("name"), "created": u.get("created")}
            for u in get_users()
        ]})
    body = request.get_json(silent=True) or {}
    if request.method == "POST":
        username = (body.get("username") or "").strip()
        name = (body.get("name") or "").strip()
        password = body.get("password") or ""
        if not username or not password:
            return jsonify({"error": "missing", "reason": "اسم المستخدم وكلمة المرور مطلوبان"}), 400
        if len(password) < 4:
            return jsonify({"error": "weak", "reason": "كلمة المرور قصيرة جداً (4 أحرف على الأقل)"}), 400
        if not re.match(r"^[A-Za-z0-9_.@-]{2,40}$", username):
            return jsonify({"error": "bad_username", "reason": "اسم المستخدم: حروف/أرقام إنجليزية و . _ @ - فقط"}), 400
        if username == os.environ.get("ADMIN_USERNAME", "admin"):
            return jsonify({"error": "reserved", "reason": "اسم المستخدم محجوز للمدير"}), 400
        users = get_users()
        if any(u.get("username") == username for u in users):
            return jsonify({"error": "exists", "reason": "اسم المستخدم موجود مسبقاً"}), 400
        users.append({
            "username": username, "name": name or username,
            "pw_hash": generate_password_hash(password),
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        save_users(users)
        return jsonify({"success": True})
    # DELETE
    username = (body.get("username") or "").strip()
    save_users([u for u in get_users() if u.get("username") != username])
    return jsonify({"success": True})


