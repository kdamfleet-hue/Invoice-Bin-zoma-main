import os
import hmac
import json
import logging
from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify

from helpers import (
    login_required, role_required, load_logo, get_system_features, set_system_features,
    _DEFAULT_FEATURES, _audit_add, SNAPSHOT_TABLES, SNAP_LABELS, _snapshot_list,
    _restore_snapshot, _row_id, blob_get, blob_set,
    _global_blob_get, _global_blob_set
)

logger = logging.getLogger("InvoiceApp")
system_bp = Blueprint('system', __name__)

try:
    import routes.schedule_transport
except Exception:
    logger.warning("schedule_transport route not loaded")

try:
    import routes.dammam
except Exception:
    logger.warning("dammam routes not loaded")

try:
    import routes.ops_cycle
except Exception:
    logger.warning("ops_cycle routes not loaded")


@system_bp.route("/admin")
@login_required
def admin_console():
    return render_template(
        "admin_console.html",
        google_user=session.get("google_user"),
        b64_en=load_logo(),
    )


@system_bp.route("/tech_updates")
@login_required
def tech_updates_page():
    return render_template(
        "tech_updates.html",
        google_user=session.get("google_user"),
        b64_en=load_logo(),
    )


# Both pages below are linked from the sidebar on every screen but had no route at all, so
# both returned 404 — the same loss as /admin and /tech_updates. /settings matters most: it
# hosts the dated-version restore UI, so the site's data-recovery screen was unreachable.
@system_bp.route("/settings")
@login_required
def settings_page():
    return render_template(
        "settings.html",
        google_user=session.get("google_user"),
        b64_en=load_logo(),
    )


@system_bp.route("/system_commands")
@login_required
def system_commands_page():
    return render_template(
        "system_commands.html",
        google_user=session.get("google_user"),
        b64_en=load_logo(),
    )


# ── Dated version snapshots: list & restore ──────────────────────────────────
# Every write through blob_set() appends a dated snapshot (helpers._snapshot), keeping the
# last SNAP_KEEP versions per tab per branch. These four endpoints are what the Settings page
# and the "🕓 السجل الزمني" button on every data tab call to list those versions and roll back
# to one. They were lost in the blueprint extraction: the helpers stayed imported at the top of
# this file but no route ever exposed them, so every restore button in the site hit a 404 while
# snapshots kept piling up in the DB unusable — i.e. the site's only data-recovery path was
# dead exactly when it was needed. Restoring the routes does not touch any stored data; it only
# gives the operator back the ability to inspect history and choose a rollback.

def _snap_tabs():
    """[{key, label}] for every snapshotted tab, in SNAP_LABELS' (Arabic, stable) order."""
    return [{"key": t, "label": SNAP_LABELS.get(t, t)} for t in SNAP_LABELS if t in SNAPSHOT_TABLES]


def _snaps_for(tab):
    """Dated versions of one tab for the active branch, validating the tab name first."""
    if tab not in SNAPSHOT_TABLES:
        return jsonify({"success": False, "error": "unknown tab", "snapshots": []}), 400
    return jsonify({"success": True, "snapshots": _snapshot_list(tab, _row_id())})


def _do_restore():
    """Shared body for both restore endpoints. Scoped to the active branch, so a restore can
    never reach another branch's data; `tab`, when the caller sends it, must match the
    snapshot's own tab."""
    body = request.get_json(silent=True) or {}
    try:
        sid = int(body.get("id"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "bad id"}), 400
    tab = (body.get("tab") or "").strip() or None
    if tab is not None and tab not in SNAPSHOT_TABLES:
        return jsonify({"success": False, "error": "unknown tab"}), 400
    try:
        ok, info = _restore_snapshot(sid, _row_id(), require_tab=tab)
    except Exception:
        logger.exception("snapshot restore failed for id=%s tab=%s", sid, tab)
        return jsonify({"success": False, "error": "restore_failed"}), 500
    if not ok:
        return jsonify({"success": False, "error": info}), 404 if info == "not_found" else 400
    return jsonify({"success": True, "tab": info})


@system_bp.route("/api/snapshots")
@login_required
def api_snapshots():
    """Without ?tab= → the snapshottable tab list (Settings dropdown).
    With ?tab=<key> → that tab's dated versions, newest first."""
    tab = (request.args.get("tab") or "").strip()
    if not tab:
        return jsonify({"success": True, "tabs": _snap_tabs()})
    return _snaps_for(tab)


@system_bp.route("/api/snapshots/restore", methods=["POST"])
@login_required
def api_snapshots_restore():
    return _do_restore()


@system_bp.route("/api/tab_history")
@login_required
def api_tab_history():
    """Per-tab history panel (static/app_ux.js) — same data, tab always required."""
    return _snaps_for((request.args.get("tab") or "").strip())


@system_bp.route("/api/tab_history/restore", methods=["POST"])
@login_required
def api_tab_history_restore():
    return _do_restore()


# ── System features & tab permissions ────────────────────────────────────────
# The four endpoints below back the Settings screen. They were lost with the page itself,
# which left the site in a bad state: app.py's enforce_dedicated_workstation_and_tab_permissions
# still runs @before_request on EVERY request and still redirects users out of tabs based on
# `tab_permissions` / `user_account_permissions`, but nothing could read or change those values
# any more. Any restriction set earlier was locked in permanently, with no way to see it, which
# looks exactly like tabs "disappearing". Restoring these puts the controls back.
# Storage keys must match app.py exactly: "tab_permissions" and "user_account_permissions".

@system_bp.route("/api/system_features", methods=["GET", "POST"])
@login_required
def api_system_features():
    if request.method == "GET":
        return jsonify({"success": True, "features": get_system_features()})
    if session.get("role") != "admin":
        return jsonify({"success": False, "error": "غير مصرح لك (Forbidden)"}), 403
    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict) or not body:
        return jsonify({"success": False, "error": "no data"}), 400
    features = get_system_features()
    changed = []
    for key, val in body.items():
        if key in _DEFAULT_FEATURES:          # only known flags, never arbitrary keys
            features[key] = bool(val)
            changed.append(f"{key}={'مفعّل' if val else 'معطّل'}")
    if not changed:
        return jsonify({"success": False, "error": "unknown feature"}), 400
    set_system_features(features)
    _audit_add("تعديل", "إعدادات النظام", None, "، ".join(changed))
    return jsonify({"success": True, "features": features})


@system_bp.route("/api/system/tab_permissions", methods=["GET", "POST"])
@login_required
@role_required("admin")
def api_tab_permissions():
    """Global (all-accounts) tab restrictions."""
    if request.method == "GET":
        perms = _global_blob_get("tab_permissions") or {}
        return jsonify({"success": True, "permissions": {
            "dedicated_mode": perms.get("dedicated_mode", "all"),
            "disabled_tabs": perms.get("disabled_tabs", []),
        }})
    body = request.get_json(silent=True) or {}
    disabled = body.get("disabled_tabs") or []
    if not isinstance(disabled, list):
        return jsonify({"success": False, "error": "disabled_tabs must be a list"}), 400
    perms = {
        "dedicated_mode": (body.get("dedicated_mode") or "all"),
        "disabled_tabs": [str(t) for t in disabled],
    }
    _global_blob_set("tab_permissions", perms)
    _audit_add("تعديل", "صلاحيات التبويبات (عام)", len(perms["disabled_tabs"]))
    return jsonify({"success": True, "permissions": perms})


def _all_sidebar_tabs():
    """Every tab the Settings page can toggle — read from the page itself so the two never drift."""
    import re as _re
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "settings.html"),
                  encoding="utf-8") as fh:
            return set(_re.findall(r'class="tab-toggle"[^>]*data-href="([^"]+)"', fh.read()))
    except Exception:
        return set()


def _current_username():
    guser = session.get("google_user")
    gname = guser.get("name") if isinstance(guser, dict) else ""
    return session.get("user") or session.get("username") or gname or ""


@system_bp.route("/api/system/user_permissions", methods=["GET", "POST", "DELETE"])
@login_required
@role_required("admin")
def api_user_permissions():
    """Per-account tab restrictions, keyed by username.

    Guard rails, because a bad save here locks a person out of the site with no visible
    cause: an empty allow-list is refused (it would confine the account to the home page);
    an allow-list that covers every tab is stored as NO allow-list (a full list is not a
    restriction, and it would silently exclude any tab added later); and you cannot restrict
    the account you are logged in with."""
    all_perms = _global_blob_get("user_account_permissions") or {}
    if request.method == "GET":
        return jsonify({"success": True, "user_permissions": all_perms})

    body = request.get_json(silent=True) or {}
    username = (body.get("username") or "").strip()
    if not username or username == "__global__":
        return jsonify({"success": False, "error": "اسم المستخدم مطلوب"}), 400

    if request.method == "DELETE":
        removed = all_perms.pop(username, None) is not None
        _global_blob_set("user_account_permissions", all_perms)
        _audit_add("حذف", "صلاحيات حساب", None, f"إزالة كل القيود عن الحساب: {username}")
        return jsonify({"success": True, "removed": removed, "user_permissions": all_perms})

    if username == _current_username():
        return jsonify({"success": False,
                        "error": "لا يمكن تقييد الحساب الذي تستخدمه الآن — سجّل الدخول بحساب مدير آخر."}), 400

    allowed = body.get("allowed_tabs")
    if allowed is not None and not isinstance(allowed, list):
        return jsonify({"success": False, "error": "allowed_tabs must be a list"}), 400
    if allowed is not None:
        allowed = [str(t) for t in allowed]
        if not allowed:
            return jsonify({"success": False,
                            "error": "لا يمكن حفظ قائمة تبويبات فارغة — سيُحبس الحساب في الصفحة الرئيسية."}), 400
        every = _all_sidebar_tabs()
        if every and every.issubset(set(allowed)):
            allowed = None  # everything allowed == no restriction

    entry = {"dedicated_mode": (body.get("dedicated_mode") or "all")}
    if allowed is not None:
        entry["allowed_tabs"] = allowed
    if entry["dedicated_mode"] == "all" and "allowed_tabs" not in entry:
        all_perms.pop(username, None)       # nothing restricted: keep the store clean
    else:
        all_perms[username] = entry
    _global_blob_set("user_account_permissions", all_perms)
    _audit_add("تعديل", "صلاحيات حساب", None, f"الحساب: {username}")
    return jsonify({"success": True, "user_permissions": all_perms})


@system_bp.route("/api/system/create_dedicated_user", methods=["POST"])
@login_required
@role_required("admin")
def api_create_dedicated_user():
    """Create (or update) an account that is locked to a single page."""
    from werkzeug.security import generate_password_hash
    from models.schema import User, db
    import re

    body = request.get_json(silent=True) or {}
    username = (body.get("username") or "").strip()
    password = body.get("password") or ""
    mode = (body.get("dedicated_mode") or "all").strip() or "all"

    if not username or not password:
        return jsonify({"success": False, "error": "اسم المستخدم وكلمة المرور مطلوبان"}), 400
    if not re.match(r"^[A-Za-z0-9_.@-]{2,40}$", username):
        return jsonify({"success": False, "error": "اسم المستخدم: حروف/أرقام إنجليزية فقط"}), 400
    if len(password) < 4:
        return jsonify({"success": False, "error": "كلمة المرور قصيرة جداً (4 أحرف على الأقل)"}), 400

    try:
        user = User.query.filter_by(username=username).first()
        if user:
            user.password_hash = generate_password_hash(password)
            user.is_active = True
        else:
            db.session.add(User(username=username,
                                password_hash=generate_password_hash(password),
                                role="viewer", is_active=True))
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception("create_dedicated_user failed for %s", username)
        return jsonify({"success": False, "error": "تعذّر إنشاء الحساب"}), 500

    all_perms = _global_blob_get("user_account_permissions") or {}
    all_perms[username] = {"dedicated_mode": mode}
    _global_blob_set("user_account_permissions", all_perms)
    _audit_add("إضافة", "حساب مخصص", None, f"الحساب: {username} — الصفحة: {mode}")
    return jsonify({"success": True, "username": username, "dedicated_mode": mode})


@system_bp.route("/api/system/my_permissions")
@login_required
def api_my_permissions():
    """The calling account's own tab restrictions — what static/app_ux.js uses to filter the
    nav. It did not exist (404), so the menu never reflected per-account restrictions even
    though the server enforced them. Resolves identity exactly like app.py's @before_request
    enforcement so the menu and the server agree, including the settings-unlocked bypass."""
    # Mirrors app.py exactly: admins are never restricted, and the branch<N> fallback only
    # applies to branch logins, not to anyone who merely switched the active branch.
    if session.get("settings_unlocked") or session.get("is_admin"):
        return jsonify({"success": True, "dedicated_mode": "all", "disabled_tabs": []})
    guser = session.get("google_user")
    gname = guser.get("name") if isinstance(guser, dict) else ""
    username = session.get("user") or session.get("username") or gname or ""
    all_perms = _global_blob_get("user_account_permissions") or {}
    mine = all_perms.get(username) or {}
    if not mine and session.get("is_branch_user") and session.get("branch_id"):
        mine = all_perms.get(f"branch{session.get('branch_id')}") or {}
    glob = _global_blob_get("tab_permissions") or {}
    out = {
        "success": True,
        "dedicated_mode": mine.get("dedicated_mode") or glob.get("dedicated_mode") or "all",
        "disabled_tabs": glob.get("disabled_tabs", []),
    }
    if mine.get("allowed_tabs") is not None:
        out["allowed_tabs"] = mine["allowed_tabs"]
    return jsonify(out)


@system_bp.route("/api/legacy/branches")
@login_required
def api_legacy_branches():
    """Branch list for the users-admin form (templates/users_admin.html) — was a 404, so the
    branch dropdown there stayed empty. Ids come from erp_branches because that is what
    routes/auth.py stores in User.branch_id; the hardcoded helpers.BRANCHES list is only a
    fallback for an empty table."""
    from models.schema import Branch
    try:
        rows = [{"id": b.id, "name": b.name} for b in Branch.query.order_by(Branch.id).all()]
    except Exception:
        logger.exception("legacy/branches: Branch query failed")
        rows = []
    if not rows:
        from helpers import BRANCHES
        rows = [{"id": b["id"], "name": b["name"]} for b in BRANCHES]
    return jsonify({"success": True, "branches": rows})
