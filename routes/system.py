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
