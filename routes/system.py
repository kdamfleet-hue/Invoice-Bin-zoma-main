import os
import hmac
import json
import logging
from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify

from helpers import (
    login_required, load_logo, get_system_features, set_system_features,
    _DEFAULT_FEATURES, _audit_add, SNAPSHOT_TABLES, SNAP_LABELS, _snapshot_list,
    _restore_snapshot, _row_id, blob_get, blob_set
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
