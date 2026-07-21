import os
import hmac
import json
import logging
from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify

from helpers import (
    login_required, load_logo, get_system_features, set_system_features,
    _DEFAULT_FEATURES, _audit_add, SNAPSHOT_TABLES, SNAP_LABELS, _snapshot_list,
    _restore_snapshot, _row_id
)

logger = logging.getLogger("InvoiceApp")
system_bp = Blueprint('system', __name__)


@system_bp.route("/tech_updates")
@login_required
def tech_updates():
    return render_template("tech_updates.html", 
                           active_branch_id=session.get("active_branch_id", 1), 
                           active_branch=session.get("active_branch", {}), 
                           snap_tab="tech_updates")

@system_bp.route("/system_commands")
@login_required
def system_commands():
    return render_template("system_commands.html",
                           active_branch_id=session.get("active_branch_id", 1),
                           active_branch=session.get("active_branch", {}),
                           snap_tab="system_commands")

@system_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    # Locked admin tab: re-enter the MASTER_PASSWORD to open, then manage shared accounts.
    master_pass = os.environ.get("MASTER_PASSWORD")
    if not master_pass:
        logger.warning("MASTER_PASSWORD not set in env! Settings page cannot be unlocked.")
    if request.method == "POST" and "password" in request.form:
        if master_pass and hmac.compare_digest(request.form.get("password", ""), master_pass):
            session["settings_unlocked"] = True
            return redirect(url_for("system.settings"))
        return render_template("tab_lock.html", next="/settings", action="/settings",
                               error="كلمة المرور غير صحيحة")
    if not session.get("settings_unlocked"):
        return render_template("tab_lock.html", next="/settings", action="/settings")
    return render_template("settings.html", google_user=session.get("google_user"), b64_en=load_logo())


@system_bp.route("/api/system_features", methods=["GET", "POST"])
@login_required
def api_system_features():
    """Read / update system-wide feature flags (admin only)."""
    if not session.get("settings_unlocked"):
        return jsonify({"error": "locked"}), 403
    if request.method == "GET":
        return jsonify({"success": True, "features": get_system_features()})
    try:
        body = request.get_json(silent=True) or {}
        features = get_system_features()
        for key in _DEFAULT_FEATURES:
            if key in body:
                features[key] = bool(body[key])
        set_system_features(features)
        _audit_add("تحديث", "إعدادات النظام", detail="تعديل ميزات النظام")
        return jsonify({"success": True, "features": features})
    except Exception:
        logger.exception("system_features POST error")
        return jsonify({"success": False, "error": "تعذّر حفظ الإعدادات."}), 500


@system_bp.route("/api/snapshots", methods=["GET"])
@login_required
def api_snapshots():
    # Dated version history per data tab — full all-tabs list from the unlocked Settings tab.
    if not session.get("settings_unlocked"):
        return jsonify({"error": "locked"}), 403
    tab = request.args.get("tab", "")
    tabs = [{"key": k, "label": SNAP_LABELS.get(k, k)} for k in sorted(SNAPSHOT_TABLES)]
    if tab not in SNAPSHOT_TABLES:
        return jsonify({"tabs": tabs, "snapshots": []})
    return jsonify({"tabs": tabs, "label": SNAP_LABELS.get(tab, tab),
                    "snapshots": _snapshot_list(tab, _row_id())})


@system_bp.route("/api/snapshots/restore", methods=["POST"])
@login_required
def api_snapshots_restore():
    if not session.get("settings_unlocked"):
        return jsonify({"error": "locked"}), 403
    ok, info = _restore_snapshot((request.get_json(silent=True) or {}).get("id"), _row_id())
    if not ok:
        return jsonify({"error": info}), (404 if info == "not_found" else 500)
    return jsonify({"success": True})


# Per-tab version history — available INSIDE each data tab to any logged-in editor.
# Scoped to the current branch (via _row_id) AND to the requested tab.
@system_bp.route("/api/tab_history", methods=["GET"])
@login_required
def api_tab_history():
    tab = request.args.get("tab", "")
    if tab not in SNAPSHOT_TABLES:
        return jsonify({"success": False, "snapshots": []}), 400
    return jsonify({"success": True, "label": SNAP_LABELS.get(tab, tab),
                    "snapshots": _snapshot_list(tab, _row_id())})


@system_bp.route("/api/tab_history/restore", methods=["POST"])
@login_required
def api_tab_history_restore():
    body = request.get_json(silent=True) or {}
    tab = body.get("tab") or ""
    if tab not in SNAPSHOT_TABLES:
        return jsonify({"success": False, "reason": "bad_tab"}), 400
    ok, info = _restore_snapshot(body.get("id"), _row_id(), require_tab=tab)
    if not ok:
        return jsonify({"success": False, "reason": info}), (404 if info == "not_found" else 400)
    return jsonify({"success": True})
